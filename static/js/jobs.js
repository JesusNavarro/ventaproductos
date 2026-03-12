export async function startJob(script, params) {
    const res = await fetch("/jobs/start", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ script, params })
    });
    return (await res.json()).job_id;
}

export function watchJob(jobId, onProgress, onDone) {
    const timer = setInterval(async () => {
        const res = await fetch(`/jobs/${jobId}/status`);
        const data = await res.json();

        onProgress(data.progress);

        if (!data.running) {
            clearInterval(timer);
            const r = await fetch(`/jobs/${jobId}/result`);
            onDone(await r.json());
        }
    }, 1000);    // milliseconds
}