from pymusicbrainz import AsyncSession
from pathlib import Path
import pytest

data_dir = Path(__file__).parent / "data" / "artist"


@pytest.mark.asyncio
async def test_mbxml_artist():
    async with AsyncSession() as session:
        metadata = await session._load_xml(
            data_dir / "0e43fe9d-c472-4b62-be9e-55f971a023e1-aliases.xml"
        )

        artist = metadata["artist"]
        assert artist["id"] == "0e43fe9d-c472-4b62-be9e-55f971a023e1"
        assert artist["type"] == "Person"
        assert artist["name"] == "Сергей Сергеевич Прокофьев"
        assert artist["sort-name"] == "Prokofiev, Sergei Sergeyevich"
        assert artist["disambiguation"] == "Russian composer"
        assert artist["gender"]["data"] == "Male"
        assert artist["country"] == "RU"
        assert artist["isni-list"]["data"][0] == "0000000121389711"

        area = artist["area"]
        assert area["id"] == "1f1fc3a4-9500-39b8-9f10-f0a465557eef"
        assert area["name"] == "Russia"
        assert area["sort-name"] == "Russia"
        assert area["iso-3166-1-code-list"]["data"][0] == "RU"

        begin_area = artist["begin-area"]
        assert begin_area["id"] == "ddac529d-ab44-4963-a04d-55c6edaf90ff"
        assert begin_area["name"] == "Sontsivka"

        aliases = artist["alias-list"]
        assert len(aliases["data"]) == 34

        alias0 = aliases["data"][0]
        assert alias0["data"] == "Prokefiev"

        # assert artist[""] == ""
