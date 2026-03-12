import subprocess, threading, uuid, json, os, csv
from config import PROCESS_TMP_PATH, PROCESS_LOG_PATH, PROCESS_JOBS_PATH, PROCESS_LOG_DELETE
from io import StringIO

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

class JobManager:
    def __init__(self):
        self.jobs = {}

    def cleanup_job(self, job):
        print(PROJECT_ROOT)
        #for path in job.get("temp_files", []):
        for path in job.get("temp_files", {}).values():
            try:
                os.remove(path)
                print("Cleaned up temp file:", path)
            except FileNotFoundError:
                pass
        if PROCESS_LOG_DELETE and job["exitCode"]==0:
            log = job.get("log_file")
            if log:
                try:
                    os.remove(log)
                    print("Cleaned up log file:", log)
                except FileNotFoundError:
                    pass

    def start(self, script, params):
        job_id = str(uuid.uuid4())
        log_file = os.path.join(PROCESS_LOG_PATH, f"{job_id}_{script}.txt")

        archivos = params.pop("archivos_texto", None)
        temp_files = {}

        if archivos:
            for name, content in archivos.items():
                safe_name = os.path.basename(name)
                path = os.path.join(PROCESS_TMP_PATH,f"{job_id}_{safe_name}.tsv")
                inputType = JobManager._detect_input_type(content)
                if inputType=="tsv":
                    pass
                if inputType=="json":
                    content = json.loads(content)
                    inputType="dictList"
                if inputType=="dictList":
                    content = JobManager._dict_list_to_tsv(content)
                with open(path, "w", encoding="utf-16") as f:
                    f.write(content)
                temp_files[name] = path

        params["temp_files"] = temp_files  # paths only

        job = {
            "id": job_id,
            "progress": 0,
            "running": True,
            "result": None,
            "log_file": log_file,
            "temp_files" : temp_files,
            "script" : script,
            "params": params
        }

        self.jobs[job_id] = job

        #script_path = os.path.join(PROCESS_JOBS_PATH, script)
        script_path = f"procesos.jobs.{script}" 

        process = subprocess.Popen(
            ["python3", "-m", script_path, json.dumps(params)],
            #stdin=subprocess.PIPE,
            cwd=PROJECT_ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        # Send large data ONLY if present
        # if archivo_texto is not None:
        #     process.stdin.write(archivo_texto)
        # process.stdin.close()

        def reader():
            with open(log_file, "w", encoding="utf-8") as lf:
                for line in process.stdout:
                    lf.write(line)
                    line = line.strip()
                    if line.startswith("PROGRESS:"):
                        job["progress"] = int(line.split(":")[1])
                    elif line.startswith("RESULT:"):
                        job["result"] = json.loads(line[7:])
            # Process is fully done here
            exit_code = process.wait()
            job["exitCode"] = exit_code
            job["running"] = False
            self.cleanup_job(job)

        threading.Thread(target=reader, daemon=True).start()
        return job_id

    def status(self, job_id):
        return self.jobs.get(job_id)

    def result(self, job_id):
        job = self.jobs.get(job_id)
        if job and not job["running"]:
            return job #job["result"]

    @staticmethod
    def _detect_input_type(data):
        """
        Returns one of:
        - "records"   → list[dict]
        - "json_text" → string containing JSON
        - "tsv_text"  → string containing TSV
        """

        # 1️⃣ List of dictionaries
        if isinstance(data, list) and all(isinstance(x, dict) for x in data):
            return "dictList"

        # 2️⃣ String → JSON or TSV
        if isinstance(data, str):
            s = data.strip()

            # Try JSON first
            if (s.startswith("{") or s.startswith("[")):
                try:
                    json.loads(s)
                    return "json"
                except json.JSONDecodeError:
                    pass

            # Otherwise treat as TSV text
            return "tsv"

        raise TypeError(f"Unsupported input type: {type(data)}")

    @staticmethod
    def _dict_list_to_tsv(records, columns=None):
        """
        Convert a list of dictionaries into TSV text (UTF-16 compatible).
        Returns a *string* (not bytes).
        """
        if not records and not columns:
            return ""
        if columns is None:
            # Preserve column order from first record
            columns = list(records[0].keys())
        output = StringIO()
        writer = csv.DictWriter(
            output,
            fieldnames=columns,
            delimiter="\t",
            lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(records)
        return output.getvalue()