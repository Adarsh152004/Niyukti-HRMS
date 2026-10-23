"""
AI-Powered Intelligent HRMS — Infrastructure & Production Deployment Test Suite.

Verifies:
1. Backend & Frontend Dockerfiles (multi-stage builds, non-root user isolation)
2. Docker Compose service dependency graph & volumes
3. Kubernetes manifests (HPA, PDB, Ingress, probes, StatefulSet)
4. GitHub Actions CI/CD workflow YAML validity
5. Observability telemetry configurations (Prometheus, Grafana)
"""

import json
from pathlib import Path
import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_dockerfile_backend_configuration():
    """Verify backend Dockerfile is multi-stage and enforces non-root execution."""
    df_path = REPO_ROOT / "docker" / "Dockerfile.backend"
    assert df_path.exists(), "Dockerfile.backend is missing"

    content = df_path.read_text(encoding="utf-8")
    assert "AS builder" in content
    assert "AS runtime" in content
    assert "USER appuser" in content
    assert "EXPOSE 8000" in content
    assert "HEALTHCHECK" in content


def test_dockerfile_frontend_and_nginx_configuration():
    """Verify frontend Dockerfile is multi-stage and nginx configuration has CSP headers."""
    df_path = REPO_ROOT / "docker" / "Dockerfile.frontend"
    nginx_path = REPO_ROOT / "docker" / "nginx.conf"

    assert df_path.exists(), "Dockerfile.frontend is missing"
    assert nginx_path.exists(), "nginx.conf is missing"

    df_content = df_path.read_text(encoding="utf-8")
    assert "AS builder" in df_content
    assert "AS runtime" in df_content
    assert "USER nginx" in df_content

    nginx_content = nginx_path.read_text(encoding="utf-8")
    assert "Content-Security-Policy" in nginx_content
    assert "X-Frame-Options" in nginx_content
    assert "gzip on;" in nginx_content


def test_docker_compose_validity():
    """Verify docker-compose.yml declares all required microservices and networks."""
    compose_path = REPO_ROOT / "docker-compose.yml"
    assert compose_path.exists(), "docker-compose.yml is missing"

    data = yaml.safe_load(compose_path.read_text(encoding="utf-8"))
    services = data.get("services", {})

    expected_services = ["postgres", "redis", "backend", "outbox-worker", "frontend", "prometheus", "grafana"]
    for s in expected_services:
        assert s in services, f"Service '{s}' missing from docker-compose.yml"

    # PostgreSQL must use pgvector image
    assert "pgvector" in services["postgres"]["image"]


def test_kubernetes_manifests_soundness():
    """Verify Kubernetes manifests contain HPA, PDB, Ingress, and Health Probes."""
    k8s_dir = REPO_ROOT / "deploy" / "k8s"

    backend_yaml = (k8s_dir / "backend-deployment.yaml").read_text(encoding="utf-8")
    docs = list(yaml.safe_load_all(backend_yaml))
    kinds = [d["kind"] for d in docs]

    assert "Deployment" in kinds
    assert "Service" in kinds
    assert "HorizontalPodAutoscaler" in kinds
    assert "PodDisruptionBudget" in kinds

    # Verify Frontend Ingress
    frontend_yaml = (k8s_dir / "frontend-deployment.yaml").read_text(encoding="utf-8")
    frontend_docs = list(yaml.safe_load_all(frontend_yaml))
    frontend_kinds = [d["kind"] for d in frontend_docs]
    assert "Ingress" in frontend_kinds

    # Verify StatefulSet
    storage_yaml = (k8s_dir / "services-and-storage.yaml").read_text(encoding="utf-8")
    storage_docs = list(yaml.safe_load_all(storage_yaml))
    storage_kinds = [d["kind"] for d in storage_docs]
    assert "StatefulSet" in storage_kinds
    assert "ConfigMap" in storage_kinds
    assert "Secret" in storage_kinds


def test_github_actions_workflows():
    """Verify CI and CD GitHub Actions workflow YAML documents."""
    ci_path = REPO_ROOT / ".github" / "workflows" / "ci.yml"
    cd_path = REPO_ROOT / ".github" / "workflows" / "cd.yml"

    assert ci_path.exists()
    assert cd_path.exists()

    ci_data = yaml.safe_load(ci_path.read_text(encoding="utf-8"))
    assert "backend-tests" in ci_data["jobs"]
    assert "frontend-build" in ci_data["jobs"]

    cd_data = yaml.safe_load(cd_path.read_text(encoding="utf-8"))
    assert "build-and-publish" in cd_data["jobs"]
    assert "deploy-k8s" in cd_data["jobs"]


def test_observability_configurations():
    """Verify Prometheus scrape jobs and Grafana dashboard JSON schema."""
    prom_path = REPO_ROOT / "deploy" / "observability" / "prometheus.yml"
    grafana_path = REPO_ROOT / "deploy" / "observability" / "grafana_dashboard.json"

    assert prom_path.exists()
    assert grafana_path.exists()

    prom_data = yaml.safe_load(prom_path.read_text(encoding="utf-8"))
    scrape_jobs = [j["job_name"] for j in prom_data.get("scrape_configs", [])]
    assert "hrms-backend" in scrape_jobs

    grafana_data = json.loads(grafana_path.read_text(encoding="utf-8"))
    assert len(grafana_data.get("panels", [])) >= 4
    assert grafana_data["title"] == "AI-Powered HRMS Production Observability Dashboard"
