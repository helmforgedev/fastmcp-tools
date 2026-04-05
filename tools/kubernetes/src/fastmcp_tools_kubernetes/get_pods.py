"""List pods in a Kubernetes namespace.

Requires: kubernetes
"""

__tags__ = ["kubernetes", "read"]
__timeout__ = 30.0


def get_pods(namespace: str = "default", label_selector: str = "") -> str:
    """List pods in a namespace with their status."""
    from kubernetes import client, config

    try:
        config.load_incluster_config()
    except config.ConfigException:
        config.load_kube_config()

    v1 = client.CoreV1Api()
    kwargs = {"namespace": namespace}
    if label_selector:
        kwargs["label_selector"] = label_selector

    pods = v1.list_namespaced_pod(**kwargs)

    lines = [f"Pods in namespace '{namespace}':"]
    for pod in pods.items:
        status = pod.status.phase
        restarts = sum(cs.restart_count for cs in (pod.status.container_statuses or []))
        lines.append(f"  {pod.metadata.name}  {status}  restarts={restarts}")

    if len(lines) == 1:
        lines.append("  (no pods found)")

    return "\n".join(lines)
