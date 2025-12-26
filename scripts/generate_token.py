#!/usr/bin/env python3
"""
Gerador de Token JWT para Admin Bootstrap

Uso:
    python scripts/generate_token.py --role admin --tenant global_admin --days 90
"""

import sys
import os
import argparse
from datetime import timedelta

# Adiciona src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.interface.api.auth import create_access_token


def generate_token(tenant_id: str, user_id: str, role: str, expires_days: int = 30) -> str:
    """
    Gera token JWT para bootstrap ou testes

    Args:
        tenant_id: UUID do tenant
        user_id: Email ou ID do usuário
        role: Role RBAC (admin, dev, auditor, app)
        expires_days: Dias até expiração

    Returns:
        JWT token string
    """
    valid_roles = ["admin", "dev", "auditor", "app"]
    if role not in valid_roles:
        raise ValueError(f"Role deve ser um de: {valid_roles}")

    token = create_access_token(
        data={
            "tenant_id": tenant_id,
            "user_id": user_id,
            "role": role
        },
        expires_delta=timedelta(days=expires_days)
    )

    return token


def main():
    parser = argparse.ArgumentParser(
        description="Gera JWT token para BuildToValue",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  # Token de admin (90 dias)
  python scripts/generate_token.py --role admin --tenant global_admin --days 90

  # Token de desenvolvedor (30 dias)
  python scripts/generate_token.py --role dev --tenant 550e8400-e29b-41d4-a716-446655440000 --user dev@company.com

  # Token de app (7 dias)
  python scripts/generate_token.py --role app --tenant 550e8400-e29b-41d4-a716-446655440000 --days 7
        """
    )

    parser.add_argument(
        "--tenant",
        default="global_admin",
        help="Tenant ID (UUID v4)"
    )
    parser.add_argument(
        "--user",
        default="root",
        help="User ID (email ou username)"
    )
    parser.add_argument(
        "--role",
        required=True,
        choices=["admin", "dev", "auditor", "app"],
        help="Role RBAC"
    )
    parser.add_argument(
        "--days",
        type=int,
        default=30,
        help="Dias até expiração (default: 30)"
    )

    args = parser.parse_args()

    try:
        token = generate_token(args.tenant, args.user, args.role, args.days)

        print(f"\n{'=' * 80}")
        print(f"🔐 BuildToValue JWT Token Generated")
        print(f"{'=' * 80}")
        print(f"Tenant ID: {args.tenant}")
        print(f"User ID:   {args.user}")
        print(f"Role:      {args.role}")
        print(f"Expira em: {args.days} dias")
        print(f"\n{'-' * 80}")
        print(f"Token:")
        print(f"{token}")
        print(f"{'-' * 80}")
        print(f"\nUso:")
        print(f"  export BTV_TOKEN='{token}'")
        print(f"  curl -H 'Authorization: Bearer $BTV_TOKEN' http://localhost:8000/health")
        print(f"{'=' * 80}\n")

    except Exception as e:
        print(f"❌ Erro ao gerar token: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
