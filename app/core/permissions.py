from fastapi import Depends, HTTPException, status

from app.core.deps import get_current_user
from app.models.db_models import UsuarioDB


def exigir_perfis(*perfis_permitidos: str):
    """
    Permite o acesso somente aos perfis informados.
    Retorna 403 quando o usuário está autenticado,
    mas não possui a permissão necessária.
    """
    permitidos = {
        perfil.strip().casefold()
        for perfil in perfis_permitidos
    }

    def verificar_perfil(
        usuario: UsuarioDB = Depends(get_current_user)
    ):
        perfil_usuario = (usuario.tipo or "").strip().casefold()

        if perfil_usuario not in permitidos:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você não tem permissão para realizar esta operação."
            )

        return usuario

    return verificar_perfil
