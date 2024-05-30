data "aws_ssm_parameter" "db_url" {
  name = "/cryoet-prod/hasura_api_db_url"
}

data "aws_ssm_parameter" "admin_pw" {
  name = "/cryoet-dev/hasura_admin_console_password"
}

module "stack" {
  source           = "git@github.com:chanzuckerberg/happy//terraform/modules/happy-stack-eks?ref=main"
  image_tag        = var.image_tag
  image_tags       = jsondecode(var.image_tags)
  app_name         = "cryoet"
  stack_name       = var.stack_name
  deployment_stage = "prod"
  stack_prefix     = "/${var.stack_name}"
  k8s_namespace    = var.k8s_namespace
  additional_env_vars = {
    HASURA_GRAPHQL_ENABLE_CONSOLE = "false"
    HASURA_GRAPHQL_DATABASE_URL = data.aws_ssm_parameter.db_url.value
    HASURA_GRAPHQL_ADMIN_SECRET = data.aws_ssm_parameter.admin_pw.value
    HASURA_GRAPHQL_UNAUTHORIZED_ROLE = "anonymous"
  }
  services = {
    cryoet-api = {
      name              = "cryoet-api",
      desired_count     = 2,
      max_count         = 5,
      port              = 8080,
      memory            = "1500Mi"
      cpu               = "1500m"
      health_check_path = "/healthz",
      service_type      = "EXTERNAL",
      platform_architecture = "arm64",
    }
  }
  tasks = {
  }
}
