module "syncer_ecr_irsa_role" {
  source  = "terraform-aws-modules/iam/aws//modules/iam-role-for-service-accounts-eks"
  version = "5.39.0"

  role_name                  = "image-syncer"
  
  oidc_providers = {
    main = {
      provider_arn               = <CLUSTER-OIDC-connect-provider-arn>
      namespace_service_accounts = ["test:py-syncer"]
    }
  }
  
  role_policy_arns = {
    policy = module.ecr_iam_policy.arn
  }
}

module "ecr_iam_policy" {
  source = "terraform-aws-modules/iam/aws//modules/iam-policy"

  name        = "access-policy"
  path        = "/"
  description = "used for creating repo and pushing images to ECR"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ecr:GetRegistryPolicy",
          "ecr:CreateRepository",
          "ecr:DescribeRegistry",
          "ecr:DescribePullThroughCacheRules",
          "ecr:PutRegistryScanningConfiguration",
          "ecr:DeleteRegistryPolicy",
          "ecr:PutRegistryPolicy",
          "ecr:GetRegistryScanningConfiguration",
          "ecr:PutReplicationConfiguration",
          "ecr:PutLifecyclePolicy",
          "ecr:PutImageTagMutability",
          "ecr:GetLifecyclePolicyPreview",
          "ecr:PutImageScanningConfiguration",
          "ecr:ListTagsForResource",
          "ecr:BatchGetRepositoryScanningConfiguration",
          "ecr:DeleteLifecyclePolicy",
          "ecr:DeleteRepository",
          "ecr:UntagResource",
          "ecr:SetRepositoryPolicy",
          "ecr:TagResource",
          "ecr:DescribeRepositories",
          "ecr:StartLifecyclePolicyPreview",
          "ecr:DeleteRepositoryPolicy",
          "ecr:GetRepositoryPolicy",
          "ecr:GetLifecyclePolicy",
          "ecr:GetAuthorizationToken",
          "ecr:InitiateLayerUpload",
          "ecr:UploadLayerPart",
          "ecr:CompleteLayerUpload",
          "ecr:BatchGetImage",
          "ecr:BatchCheckLayerAvailability",
          "ecr:GetDownloadUrlForLayer",
          "ecr:PutImage"
        ]
        Resource = "*"
      }
    ]
  })
}