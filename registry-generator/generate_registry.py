import dataclasses
import json
import os
from dataclasses import dataclass, field
from pathlib import Path

REPOSITORY_NAME = os.getenv("GITHUB_REPOSITORY", "test/repo")
REPOSITORY_OWNER = REPOSITORY_NAME.split("/")[0]
GITHUB_RAW_URL = "https://raw.githubusercontent.com"
CHECK_CONDITION = ["*compose.y*ml", ".env.example", "README.md"]
JSON_SCHEMA_URL = "https://registry.getarcane.app/schema.json"


@dataclass
class ComposeTemplate:
    id: str
    name: str
    description: str
    version: str
    author: str
    compose_url: str
    env_url: str
    documentation_url: str
    tags: list[str] = field(default_factory=lambda: ["app"])


@dataclass
class RegistryStruct:
    name: str = "Arcane Registry Template"
    description: str = "Registry for Arcane for docker compose file management"
    version: str = "1.0.0"
    author: str = REPOSITORY_OWNER
    url: str = f"https://github.com/{REPOSITORY_NAME}"
    templates: list[ComposeTemplate] = field(default_factory=list)


def generate_registry_file(registry_path: Path, registry: RegistryStruct):
    json_schema = {"$schema": JSON_SCHEMA_URL, **dataclasses.asdict(registry)}
    with open(registry_path, "w") as f:
        json.dump(json_schema, f, indent=4)


def populate_templates() -> list[ComposeTemplate]:
    templates = []
    templates_dir = Path("templates")
    for template_dir in templates_dir.iterdir():
        if template_dir.is_dir():
            if compose_file := list(template_dir.glob("*compose.y*ml")):
                if not list(template_dir.glob("*.env.example")):
                    Path(f"{template_dir}/.env.example").touch()

                if not list(template_dir.glob("README.md")):
                    Path(f"{template_dir}/README.md").touch()

                templates.append(
                    ComposeTemplate(
                        id=template_dir.name,
                        name=template_dir.name,
                        description=template_dir.name,
                        version="1.0.0",
                        author=REPOSITORY_OWNER,
                        compose_url=f"{GITHUB_RAW_URL}/{REPOSITORY_NAME}/refs/heads/main/templates/{template_dir.name}/{compose_file[0].name}",
                        env_url=f"{GITHUB_RAW_URL}/{REPOSITORY_NAME}/refs/heads/main/templates/{template_dir.name}/.env.example",
                        documentation_url=f"{GITHUB_RAW_URL}/{REPOSITORY_NAME}/refs/heads/main/templates/{template_dir.name}/README.md",
                        tags=["app"],
                    )
                )
    return templates


def main():
    templates = populate_templates()
    registry = RegistryStruct(templates=templates)
    generate_registry_file(Path("arcane-registry.json"), registry)


# def test():
#     templates_dir = Path("templates")
#     for template_dir in templates_dir.iterdir():
#         if template_dir.is_dir():
#             conditions_met = [
#                 list(template_dir.glob(condition)) for condition in CHECK_CONDITION
#             ]
#             print(conditions_met[0][0].name)
#             if all(conditions_met):
#                 print(f"Template '{template_dir.name}' meets all conditions.")


if __name__ == "__main__":
    main()
