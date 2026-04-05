"""Get pod logs from Kubernetes.

Requires: kubernetes
"""

__tags__ = ["kubernetes", "read"]
__timeout__ = 30.0


def get_logs(
    pod_name: str,
    namespace: str = "default",
    container: str = "",
    tail_lines: int = 100,
) -> str:
    """Get logs from a pod, optionally from a specific container."""
    from kubernetes import client, config

    try:
        config.load_incluster_config()
    except config.ConfigException:
        config.load_kube_config()

    v1 = client.CoreV1Api()
    kwargs = {
        "name": pod_name,
        "namespace": namespace,
        "tail_lines": tail_lines,
    }
    if container:
        kwargs["container"] = container

    logs = v1.read_namespaced_pod_log(**kwargs)
    return logs or "(no logs)"
