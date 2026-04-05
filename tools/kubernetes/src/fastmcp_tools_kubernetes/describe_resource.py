"""Describe a Kubernetes resource.

Requires: kubernetes
"""

__tags__ = ["kubernetes", "read"]
__timeout__ = 30.0


def describe_resource(
    kind: str,
    name: str,
    namespace: str = "default",
) -> str:
    """Get detailed information about a Kubernetes resource."""
    from kubernetes import client, config

    try:
        config.load_incluster_config()
    except config.ConfigException:
        config.load_kube_config()

    kind_lower = kind.lower()

    if kind_lower in ("pod", "pods"):
        v1 = client.CoreV1Api()
        obj = v1.read_namespaced_pod(name, namespace)
    elif kind_lower in ("service", "services", "svc"):
        v1 = client.CoreV1Api()
        obj = v1.read_namespaced_service(name, namespace)
    elif kind_lower in ("deployment", "deployments", "deploy"):
        apps = client.AppsV1Api()
        obj = apps.read_namespaced_deployment(name, namespace)
    elif kind_lower in ("configmap", "configmaps", "cm"):
        v1 = client.CoreV1Api()
        obj = v1.read_namespaced_config_map(name, namespace)
    elif kind_lower in ("secret", "secrets"):
        v1 = client.CoreV1Api()
        obj = v1.read_namespaced_secret(name, namespace)
    else:
        return f"Unsupported resource kind: {kind}"

    meta = obj.metadata
    lines = [
        f"Kind: {kind}",
        f"Name: {meta.name}",
        f"Namespace: {meta.namespace}",
        f"Created: {meta.creation_timestamp}",
        f"Labels: {meta.labels or {}}",
        f"Annotations: {len(meta.annotations or {})} annotation(s)",
    ]

    if hasattr(obj, "status") and hasattr(obj.status, "phase"):
        lines.append(f"Status: {obj.status.phase}")

    return "\n".join(lines)
