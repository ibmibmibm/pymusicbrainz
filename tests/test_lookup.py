from pymusicbrainz import Session, AsyncSession
import pytest


@pytest.mark.asyncio
async def test_artist_async():
    async with AsyncSession() as session:
        with pytest.raises(ValueError) as excinfo:
            artist = await session.lookup_artist(id="blah")
        assert "Invalid id" in str(excinfo.value)

        artist = await session.lookup_artist(
            id="89ad4ac3-39f7-470e-963a-56509c546377"
        )
        assert artist["id"] == "89ad4ac3-39f7-470e-963a-56509c546377"
        assert artist["type"] == "Other"
        assert artist["type-id"] == "ac897045-5043-3294-969b-187360e45d86"
        assert artist["name"] == "Various Artists"
        assert artist["sort-name"] == "Various Artists"
        assert artist["disambiguation"] == "add compilations to this artist"

        artist = await session.lookup_artist(
            id="89ad4ac3-39f7-470e-963a-56509c546377",
            includes=["aliases", "annotation", "genres", "ratings", "tags"],
        )
        assert artist["id"] == "89ad4ac3-39f7-470e-963a-56509c546377"
        assert artist["type"] == "Other"
        assert artist["type-id"] == "ac897045-5043-3294-969b-187360e45d86"
        assert artist["name"] == "Various Artists"
        assert artist["sort-name"] == "Various Artists"
        assert artist["disambiguation"] == "add compilations to this artist"
        for alias in artist["alias-list"]["data"]:
            assert alias["data"] is not None
        for genre in artist["genre-list"]["data"]:
            assert genre["name"] is not None
        for tag in artist["tag-list"]["data"]:
            assert tag["name"] is not None
        assert artist["rating"] is not None

        artist = await session.lookup_artist(
            id="89ad4ac3-39f7-470e-963a-56509c546377",
            includes=[
                "area-rels",
                "artist-rels",
                "event-rels",
                "instrument-rels",
                "label-rels",
                "place-rels",
                "recording-rels",
                "release-group-rels",
                "release-rels",
                "series-rels",
                "url-rels",
                "work-rels",
            ],
        )
        assert artist["id"] == "89ad4ac3-39f7-470e-963a-56509c546377"
        assert artist["type"] == "Other"
        assert artist["type-id"] == "ac897045-5043-3294-969b-187360e45d86"
        assert artist["name"] == "Various Artists"
        assert artist["sort-name"] == "Various Artists"
        assert artist["disambiguation"] == "add compilations to this artist"
        for relation in artist["relation-list"]:
            assert relation["target-type"] is not None
            assert relation["data"] is not None


def test_artist():
    with Session() as session:
        with pytest.raises(ValueError) as excinfo:
            artist = session.lookup_artist(id="blah")
        assert "Invalid id" in str(excinfo.value)

        artist = session.lookup_artist(
            id="89ad4ac3-39f7-470e-963a-56509c546377"
        )
        assert artist["id"] == "89ad4ac3-39f7-470e-963a-56509c546377"
        assert artist["type"] == "Other"
        assert artist["type-id"] == "ac897045-5043-3294-969b-187360e45d86"
        assert artist["name"] == "Various Artists"
        assert artist["sort-name"] == "Various Artists"
        assert artist["disambiguation"] == "add compilations to this artist"

        artist = session.lookup_artist(
            id="89ad4ac3-39f7-470e-963a-56509c546377",
            includes=["aliases", "annotation", "genres", "ratings", "tags"],
        )
        assert artist["id"] == "89ad4ac3-39f7-470e-963a-56509c546377"
        assert artist["type"] == "Other"
        assert artist["type-id"] == "ac897045-5043-3294-969b-187360e45d86"
        assert artist["name"] == "Various Artists"
        assert artist["sort-name"] == "Various Artists"
        assert artist["disambiguation"] == "add compilations to this artist"
        for alias in artist["alias-list"]["data"]:
            assert alias["data"] is not None
        for genre in artist["genre-list"]["data"]:
            assert genre["name"] is not None
        for tag in artist["tag-list"]["data"]:
            assert tag["name"] is not None
        assert artist["rating"] is not None


@pytest.mark.asyncio
async def test_recording_async():
    async with AsyncSession() as session:
        with pytest.raises(ValueError) as excinfo:
            recording = await session.lookup_recording(id="blah")
        assert "Invalid id" in str(excinfo.value)

        recording = await session.lookup_recording(
            id="f606f733-c1eb-43f3-93c1-71994ea611e3",
        )
        assert recording["id"] == "f606f733-c1eb-43f3-93c1-71994ea611e3"
        assert recording["title"] == "Shades of Gray"
        assert recording["length"] == 259600

        recording = await session.lookup_recording(
            id="f606f733-c1eb-43f3-93c1-71994ea611e3",
            includes=[
                "aliases",
                "annotation",
                "artists",
                "genres",
                "ratings",
                "releases",
                "tags",
            ],
        )
        assert recording["id"] == "f606f733-c1eb-43f3-93c1-71994ea611e3"
        assert recording["title"] == "Shades of Gray"
        assert recording["length"] == 259600
        artist = recording["artist-credit"]["data"][0]["artist"]
        assert artist["id"] == "83c6ecce-ebc2-4064-ad28-49c7354469f4"
        release = recording["release-list"]["data"][0]
        assert release["title"] == "Shades of Gray"
