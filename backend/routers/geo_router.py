from fastapi import APIRouter

router = APIRouter()

@router.get("/elevation", summary="Obter elevação de um ponto (placeholder)")
def get_elevation():
    return {"message": "Endpoint de dados geográficos a ser implementado."}