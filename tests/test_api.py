"""Testes do cliente API."""

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from src.api.pncp_client import PNCPClient


class TestPNCPClient:
    """Testes para PNCPClient."""

    def test_gerar_intervalos_mensais_1_mes(self) -> None:
        """Gera 1 intervalo para 1 mês."""
        intervalos = PNCPClient.gerar_intervalos_mensais(1)

        assert len(intervalos) == 1
        assert len(intervalos[0]) == 2

    def test_gerar_intervalos_mensais_3_meses(self) -> None:
        """Gera 3 intervalos para 3 meses."""
        intervalos = PNCPClient.gerar_intervalos_mensais(3)

        assert len(intervalos) == 3

    def test_intervalos_formato_data(self) -> None:
        """Formato de data correto (YYYYMMDD)."""
        intervalos = PNCPClient.gerar_intervalos_mensais(1)
        inicio, fim = intervalos[0]

        assert len(inicio) == 8
        assert len(fim) == 8
        assert inicio.isdigit()
        assert fim.isdigit()

    @pytest.mark.asyncio
    async def test_parse_item(self, api_response_mock: dict) -> None:
        """Parse de item da API."""
        client = PNCPClient()
        item = api_response_mock["data"][0]

        licitacao = client._parse_item(item)

        assert licitacao.numero_pncp == "12345678000190-1-000001/2024"
        assert "georreferenciamento" in licitacao.objeto.lower()
        assert licitacao.valor_estimado == 50000.0
        assert licitacao.municipio == "Campinas"
        assert licitacao.uf == "SP"

    @pytest.mark.asyncio
    async def test_buscar_pagina_timeout(self) -> None:
        """Retorna None em timeout."""
        async with PNCPClient() as client:
            with patch.object(
                client._client, "get", new_callable=AsyncMock
            ) as mock_get:
                mock_get.side_effect = httpx.TimeoutException("timeout")

                result = await client.buscar_pagina("SP", "20240101", "20240131", 6)

                assert result is None

    @pytest.mark.asyncio
    async def test_buscar_pagina_http_error(self) -> None:
        """Retorna None em erro HTTP."""
        async with PNCPClient() as client:
            with patch.object(
                client._client, "get", new_callable=AsyncMock
            ) as mock_get:
                mock_response = MagicMock()
                mock_response.status_code = 500
                mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
                    "Internal Server Error",
                    request=MagicMock(),
                    response=mock_response,
                )
                mock_get.return_value = mock_response

                result = await client.buscar_pagina("SP", "20240101", "20240131", 6)

                assert result is None

    @pytest.mark.asyncio
    async def test_buscar_pagina_request_error(self) -> None:
        """Retorna None em erro de conexão."""
        async with PNCPClient() as client:
            with patch.object(
                client._client, "get", new_callable=AsyncMock
            ) as mock_get:
                mock_get.side_effect = httpx.RequestError("Connection failed")

                result = await client.buscar_pagina("SP", "20240101", "20240131", 6)

                assert result is None

    @pytest.mark.asyncio
    async def test_buscar_pagina_success(self, api_response_mock: dict) -> None:
        """Retorna dados em sucesso."""
        async with PNCPClient() as client:
            with patch.object(
                client._client, "get", new_callable=AsyncMock
            ) as mock_get:
                mock_response = MagicMock()
                mock_response.status_code = 200
                mock_response.raise_for_status = MagicMock()
                mock_response.json.return_value = api_response_mock
                mock_get.return_value = mock_response

                result = await client.buscar_pagina("SP", "20240101", "20240131", 6)

                assert result is not None
                assert "data" in result
                assert len(result["data"]) == 1
