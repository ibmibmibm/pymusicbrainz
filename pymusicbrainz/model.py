import datetime
import decimal
import enum
from collections import defaultdict, namedtuple, UserList, UserDict
from logging import getLogger

from lxml import etree

log = getLogger(__name__)


def parse_int(attrs, childs, data):
    return int(data)


def parse_str(attrs, childs, data):
    return data


def parse_bool(attrs, childs, data):
    return data == "true"


class Direction(enum.Enum):
    both = 1
    forward = 2
    backward = 3


def parse_direction(attrs, childs, data):
    return Direction.__members__[data]


class Quality(enum.Enum):
    low = 1
    normal = 2
    high = 3


def parse_quality(attrs, childs, data):
    return Quality.__members__[data]


def list_factory(name, cls, tag):
    def __init__(self, attrs, childs, data):
        UserDict.__init__(self)
        self.data.update(attrs)
        self.data["data"] = childs[tag]

    return type(
        name, (UserDict,), {"mapping": {tag: cls}, "__init__": __init__}
    )


class Entity(UserDict):
    @staticmethod
    def valid_lookup_include(inc):
        return inc in {
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
        }


class Area(Entity):
    @staticmethod
    def init():
        Area.mapping = {
            "alias-list": AliasList,
            "annotation": Annotation,
            "disambiguation": parse_str,
            "genre-list": GenreList,
            "iso-3166-1-code-list": ISO_3166_1_CodeList,
            "iso-3166-2-code-list": ISO_3166_2_CodeList,
            "iso-3166-3-code-list": ISO_3166_3_CodeList,
            "life-span": LifeSpan,
            "name": parse_str,
            "relation-list": RelationList,
            "sort-name": parse_str,
            "tag-list": TagList,
            "user-genre-list": GenreList,
            "user-tag-list": TagList,
        }

    @staticmethod
    def valid_lookup_include(inc):
        if inc in {
            "aliases",
            "annotation",
            "genres",
            "ratings",
            "tags",
            "user-genres",
            "user-ratings",
            "user-tags",
        }:
            return True
        return Entity.valid_lookup_include(inc)

    @staticmethod
    def valid_linked(linked):
        return linked in {
            "collection",
        }

    def __init__(self, attrs, childs, data):
        super().__init__()
        self.data.update(attrs)
        for key in childs.keys():
            if key != "relation-list":
                childs[key] = childs[key][0]
        self.data.update(childs)


class Artist(Entity):
    @staticmethod
    def init():
        Artist.mapping = {
            "alias-list": AliasList,
            "annotation": Annotation,
            "area": Area,
            "begin-area": Area,
            "country": parse_str,
            "disambiguation": parse_str,
            "end-area": Area,
            "gender": Gender,
            "genre-list": GenreList,
            "ipi": parse_str,
            "ipi-list": IPIList,
            "isni-list": ISNIList,
            "life-span": LifeSpan,
            "name": parse_str,
            "rating": Rating,
            "recording-list": RecordingList,
            "relation-list": RelationList,
            "release-group-list": ReleaseGroupList,
            "release-list": ReleaseList,
            "sort-name": parse_str,
            "tag-list": TagList,
            "user-genre-list": GenreList,
            "user-rating": parse_int,
            "user-tag-list": TagList,
            "work-list": WorkList,
        }

    @staticmethod
    def valid_lookup_include(inc):
        if inc in {
            "aliases",
            "annotation",
            "genres",
            "ratings",
            "recordings",
            "release-groups",
            "releases",
            "tags",
            "user-genres",
            "user-ratings",
            "user-tags",
            "works",
        }:
            return True
        return Entity.valid_lookup_include(inc)

    @staticmethod
    def valid_linked(linked):
        return linked in {
            "area",
            "collection",
            "recording",
            "release",
            "release-group",
            "work",
        }

    def __init__(self, attrs, childs, data):
        super().__init__()
        self.data.update(attrs)
        for key in childs.keys():
            if key != "relation-list":
                childs[key] = childs[key][0]
        self.data.update(childs)


class Collection(Entity):
    @staticmethod
    def init():
        Collection.mapping = {
            "name": parse_str,
            "editor": parse_str,
            "area-list": AreaList,
            "artlist-list": ArtistList,
            "event-list": EventList,
            "instrument-list": InstrumentList,
            "label-list": LabelList,
            "place-list": PlaceList,
            "recording-list": RecordingList,
            "release-list": ReleaseList,
            "release-group-list": ReleaseGroupList,
            "series-list": SeriesList,
            "work-list": WorkList,
        }

    @staticmethod
    def valid_lookup_include(inc):
        if inc in {
            "user-collections",
        }:
            return True
        return Entity.valid_lookup_include(inc)

    @staticmethod
    def valid_linked(linked):
        return linked in {
            "area",
            "artist",
            "editor",
            "event",
            "label",
            "place",
            "recording",
            "release",
            "release-group",
            "work",
        }

    def __init__(self, attrs, childs, data):
        super().__init__()
        self.data.update(attrs)
        for key in childs.keys():
            if key != "relation-list":
                childs[key] = childs[key][0]
        self.data.update(childs)


class Event(Entity):
    @staticmethod
    def init():
        Event.mapping = {
            "alias-list": AliasList,
            "annotation": Annotation,
            "cancelled": parse_bool,
            "disambiguation": parse_str,
            "genre-list": GenreList,
            "life-span": LifeSpan,
            "name": parse_str,
            "rating": Rating,
            "relation-list": RelationList,
            "setlist": parse_str,
            "tag-list": TagList,
            "time": parse_str,
            "user-genre-list": GenreList,
            "user-rating": parse_int,
            "user-tag-list": TagList,
        }

    @staticmethod
    def valid_lookup_include(inc):
        if inc in {
            "aliases",
            "annotation",
            "genres",
            "ratings",
            "tags",
            "user-genres",
            "user-ratings",
            "user-tags",
        }:
            return True
        return Entity.valid_lookup_include(inc)

    @staticmethod
    def valid_linked(linked):
        return linked in {
            "area",
            "artist",
            "place",
            "collection",
        }

    def __init__(self, attrs, childs, data):
        super().__init__()
        self.data.update(attrs)
        for key in childs.keys():
            if key != "relation-list":
                childs[key] = childs[key][0]
        self.data.update(childs)


class Instrument(Entity):
    @staticmethod
    def init():
        Instrument.mapping = {
            "alias-list": AliasList,
            "annotation": Annotation,
            "description": parse_str,
            "disambiguation": parse_str,
            "genre-list": GenreList,
            "name": parse_str,
            "relation-list": RelationList,
            "tag-list": TagList,
            "user-genre-list": GenreList,
            "user-tag-list": TagList,
        }

    @staticmethod
    def valid_lookup_include(inc):
        if inc in {
            "aliases",
            "annotation",
            "genres",
            "tags",
            "user-genres",
            "user-tags",
        }:
            return True
        return Entity.valid_lookup_include(inc)

    @staticmethod
    def valid_linked(linked):
        return linked in {
            "collection",
        }

    def __init__(self, attrs, childs, data):
        super().__init__()
        self.data.update(attrs)
        for key in childs.keys():
            if key != "relation-list":
                childs[key] = childs[key][0]
        self.data.update(childs)


class Label(Entity):
    @staticmethod
    def init():
        Label.mapping = {
            "alias-list": AliasList,
            "annotation": Annotation,
            "area": Area,
            "country": parse_str,
            "disambiguation": parse_str,
            "genre-list": GenreList,
            "ipi": parse_str,
            "ipi-list": IPIList,
            "isni-list": ISNIList,
            "label-code": parse_int,
            "life-span": LifeSpan,
            "name": parse_str,
            "rating": Rating,
            "relation-list": RelationList,
            "release-list": ReleaseList,
            "sort-name": parse_str,
            "tag-list": TagList,
            "user-genre-list": GenreList,
            "user-rating": parse_int,
            "user-tag-list": TagList,
        }

    @staticmethod
    def valid_lookup_include(inc):
        if inc in {
            "aliases",
            "annotation",
            "genres",
            "ratings",
            "releases",
            "tags",
            "user-genres",
            "user-ratings",
            "user-tags",
        }:
            return True
        return Entity.valid_lookup_include(inc)

    @staticmethod
    def valid_linked(linked):
        return linked in {
            "area",
            "collection",
            "release",
        }

    def __init__(self, attrs, childs, data):
        super().__init__()
        self.data.update(attrs)
        for key in childs.keys():
            if key != "relation-list":
                childs[key] = childs[key][0]
        self.data.update(childs)


class Place(Entity):
    @staticmethod
    def init():
        Place.mapping = {
            "address": parse_str,
            "alias-list": AliasList,
            "annotation": Annotation,
            "area": Area,
            "coordinates": Coordinates,
            "disambiguation": parse_str,
            "genre-list": GenreList,
            "life-span": LifeSpan,
            "name": parse_str,
            "relation-list": RelationList,
            "tag-list": TagList,
            "user-genre-list": GenreList,
            "user-tag-list": TagList,
        }

    @staticmethod
    def valid_lookup_include(inc):
        if inc in {
            "aliases",
            "annotation",
            "genres",
            "tags",
            "user-genres",
            "user-tags",
        }:
            return True
        return Entity.valid_lookup_include(inc)

    @staticmethod
    def valid_linked(linked):
        return linked in {
            "area",
            "collection",
        }

    def __init__(self, attrs, childs, data):
        super().__init__()
        self.data.update(attrs)
        for key in childs.keys():
            if key != "relation-list":
                childs[key] = childs[key][0]
        self.data.update(childs)


class Recording(Entity):
    @staticmethod
    def init():
        Recording.mapping = {
            "alias-list": AliasList,
            "annotation": Annotation,
            "artist-credit": ArtistCredit,
            "disambiguation": parse_str,
            "genre-list": GenreList,
            "isrc-list": ISRCList,
            "length": parse_int,
            "puid-list": PUIDList,
            "rating": Rating,
            "relation-list": RelationList,
            "release-list": ReleaseList,
            "tag-list": TagList,
            "title": parse_str,
            "user-genre-list": GenreList,
            "user-rating": parse_int,
            "user-tag-list": TagList,
            "video": parse_bool,
        }

    @staticmethod
    def valid_lookup_include(inc):
        if inc in {
            "aliases",
            "annotation",
            "artist-credits",
            "artists",
            "genres",
            "isrcs",
            "ratings",
            "releases",
            "tags",
            "user-genres",
            "user-ratings",
            "user-tags",
            "work-level-rels",
        }:
            return True
        return Entity.valid_lookup_include(inc)

    @staticmethod
    def valid_linked(linked):
        return linked in {
            "area",
            "collection",
            "release",
            "work",
        }

    def __init__(self, attrs, childs, data):
        super().__init__()
        self.data.update(attrs)
        for key in childs.keys():
            if key != "relation-list":
                childs[key] = childs[key][0]
        self.data.update(childs)


class Release(Entity):
    @staticmethod
    def init():
        Release.mapping = {
            "alias-list": AliasList,
            "annotation": Annotation,
            "artist-credit": ArtistCredit,
            "asin": parse_str,
            "barcode": parse_str,
            "collection-list": CollectionList,
            "country": parse_str,
            "cover-art-archive": CoverArtArchive,
            "date": parse_str,
            "disambiguation": parse_str,
            "genre-list": GenreList,
            "label-info-list": LabelInfoList,
            "medium-list": MediumList,
            "packaging": Packaging,
            "quality": parse_quality,
            "relation-list": RelationList,
            "release-event-list": ReleaseEventList,
            "release-group": ReleaseGroup,
            "status": Status,
            "tag-list": TagList,
            "text-representation": TextRepresentation,
            "title": parse_str,
            "user-genre-list": GenreList,
            "user-tag-list": TagList,
        }

    @staticmethod
    def valid_lookup_include(inc):
        if inc in {
            "aliases",
            "annotation",
            "artist-credits",
            "artists",
            "collections",
            "discids",
            "genres",
            "labels",
            "media",
            "ratings",
            "recording-level-rels",
            "recordings",
            "release-groups",
            "tags",
            "user-genres",
            "user-ratings",
            "user-tags",
            "work-level-rels",
        }:
            return True
        return Entity.valid_lookup_include(inc)

    @staticmethod
    def valid_linked(linked):
        return linked in {
            "area",
            "artist",
            "collection",
            "label",
            "recording",
            "release-group",
            "track",
            "track_artist",
        }

    def __init__(self, attrs, childs, data):
        super().__init__()
        self.data.update(attrs)
        for key in childs.keys():
            if key != "relation-list":
                childs[key] = childs[key][0]
        self.data.update(childs)


class ReleaseGroup(Entity):
    @staticmethod
    def init():
        ReleaseGroup.mapping = {
            "alias-list": AliasList,
            "annotation": Annotation,
            "artist-credit": ArtistCredit,
            "disambiguation": parse_str,
            "first-release-date": parse_str,
            "genre-list": GenreList,
            "primary-type": PrimaryType,
            "rating": Rating,
            "relation-list": RelationList,
            "release-list": ReleaseList,
            "secondary-type-list": SecondaryTypeList,
            "tag-list": TagList,
            "title": parse_str,
            "user-genre-list": GenreList,
            "user-rating": parse_int,
            "user-tag-list": TagList,
        }

    @staticmethod
    def valid_lookup_include(inc):
        if inc in {
            "aliases",
            "annotation",
            "artist-credits",
            "artists",
            "genres",
            "ratings",
            "releases",
            "tags",
            "user-genres",
            "user-ratings",
            "user-tags",
        }:
            return True
        return Entity.valid_lookup_include(inc)

    @staticmethod
    def valid_linked(linked):
        return linked in {
            "artist",
            "collection",
            "release",
        }

    def __init__(self, attrs, childs, data):
        super().__init__()
        self.data.update(attrs)
        for key in childs.keys():
            if key != "relation-list":
                childs[key] = childs[key][0]
        self.data.update(childs)


class Series(Entity):
    @staticmethod
    def init():
        Series.mapping = {
            "alias-list": AliasList,
            "annotation": Annotation,
            "disambiguation": parse_str,
            "genre-list": GenreList,
            "name": parse_str,
            "ordering-attribute": parse_str,
            "relation-list": RelationList,
            "tag-list": TagList,
            "user-genre-list": GenreList,
            "user-tag-list": TagList,
        }

    @staticmethod
    def valid_lookup_include(inc):
        if inc in {
            "aliases",
            "annotation",
            "genres",
            "tags",
            "user-genres",
            "user-tags",
        }:
            return True
        return Entity.valid_lookup_include(inc)

    @staticmethod
    def valid_linked(linked):
        return linked in {
            "collection",
        }

    def __init__(self, attrs, childs, data):
        super().__init__()
        self.data.update(attrs)
        for key in childs.keys():
            if key != "relation-list":
                childs[key] = childs[key][0]
        self.data.update(childs)


class Url(Entity):
    @staticmethod
    def init():
        Url.mapping = {
            "relation-list": RelationList,
            "resource": parse_str,
        }

    @staticmethod
    def valid_linked(linked):
        return linked in {
            "resource",
        }

    def __init__(self, attrs, childs, data):
        super().__init__()
        self.data.update(attrs)
        for key in childs.keys():
            if key != "relation-list":
                childs[key] = childs[key][0]
        self.data.update(childs)


class Work(Entity):
    @staticmethod
    def init():
        Work.mapping = {
            "alias-list": AliasList,
            "annotation": Annotation,
            "artist-credit": ArtistCredit,
            "attribute-list": WorkAttributeList,
            "disambiguation": parse_str,
            "genre-list": GenreList,
            "iswc": parse_str,
            "iswc-list": ISWCList,
            "language": parse_str,
            "language-list": LanguageList,
            "rating": Rating,
            "relation-list": RelationList,
            "tag-list": TagList,
            "title": parse_str,
            "user-genre-list": GenreList,
            "user-rating": parse_int,
            "user-tag-list": TagList,
        }

    @staticmethod
    def valid_lookup_include(inc):
        if inc in {
            "aliases",
            "annotation",
            "genres",
            "ratings",
            "tags",
            "user-genres",
            "user-ratings",
            "user-tags",
        }:
            return True
        return Entity.valid_lookup_include(inc)

    @staticmethod
    def valid_linked(linked):
        return linked in {
            "artist",
            "collection",
        }

    def __init__(self, attrs, childs, data):
        super().__init__()
        self.data.update(attrs)
        for key in childs.keys():
            if key != "relation-list":
                childs[key] = childs[key][0]
        self.data.update(childs)


AreaList = list_factory("AreaList", Area, "area")
ArtistList = list_factory("ArtistList", Artist, "artist")
CollectionList = list_factory("CollectionList", Collection, "collection")
EventList = list_factory("EventList", Event, "event")
InstrumentList = list_factory("InstrumentList", Instrument, "instrument")
LabelList = list_factory("LabelList", Label, "label")
PlaceList = list_factory("PlaceList", Place, "place")
RecordingList = list_factory("RecordingList", Recording, "recording")
ReleaseGroupList = list_factory(
    "ReleaseGroupList", ReleaseGroup, "release-group"
)
ReleaseList = list_factory("ReleaseList", Release, "release")
SeriesList = list_factory("SeriesList", Series, "series")
UrlList = list_factory("URLList", Url, "url")
WorkList = list_factory("WorkList", Work, "work")


class Child(UserDict):
    def __init__(self, attrs, childs, data):
        super().__init__()
        self.data.update(attrs)
        self.data["data"] = data


class Alias(Child):
    pass


class Format(Child):
    pass


class Gender(Child):
    pass


class Offset(Child):
    pass


class Packaging(Child):
    pass


class PrimaryType(Child):
    pass


class RelationAttribute(Child):
    pass


class SecondaryType(Child):
    pass


class Status(Child):
    pass


class WorkAttribute(Child):
    pass


AliasList = list_factory("AliasList", Alias, "alias")
IPIList = list_factory("IPIList", parse_str, "ipi")
ISNIList = list_factory("ISNIList", parse_str, "isni")
ISO_3166_1_CodeList = list_factory(
    "ISO3166_1CodeList", parse_str, "iso-3166-1-code"
)
ISO_3166_2_CodeList = list_factory(
    "ISO3166_2CodeList", parse_str, "iso-3166-2-code"
)
ISO_3166_3_CodeList = list_factory(
    "ISO3166_3CodeList", parse_str, "iso-3166-3-code"
)
OffsetList = list_factory("OffsetList", Offset, "offset")
RelationAttributeList = list_factory(
    "RelationAttributeList", RelationAttribute, "attribute"
)
SecondaryTypeList = list_factory(
    "SecondaryTypeList", SecondaryType, "secondary-type"
)
WorkAttributeList = list_factory(
    "WorkAttributeList", WorkAttribute, "attribute"
)

LanguageList = list_factory("LanguageList", parse_str, "language")
ISWCList = list_factory("ISWCList", parse_str, "iswc")


class Tag(UserDict):
    mapping = {
        "name": parse_str,
    }

    def __init__(self, attrs, childs, data):
        super().__init__()
        self.data.update(attrs)
        for key in childs.keys():
            childs[key] = childs[key][0]
        self.data.update(childs)


TagList = list_factory("TagList", Tag, "tag")


class Genre(UserDict):
    mapping = {
        "name": parse_str,
        "disambiguation": parse_str,
    }

    def __init__(self, attrs, childs, data):
        super().__init__()
        self.data.update(attrs)
        for key in childs.keys():
            childs[key] = childs[key][0]
        self.data.update(childs)


GenreList = list_factory("GenreList", Genre, "genre")


class Rating(UserDict):
    mapping = {
        "votes-count": parse_int,
    }

    def __init__(self, attrs, childs, data):
        super().__init__()
        self.data.update(attrs)
        self.data["data"] = decimal.Decimal(data)


class LabelInfo(UserDict):
    mapping = {
        "catalog-number": parse_str,
        "label": Label,
    }

    def __init__(self, attrs, childs, data):
        super().__init__()
        self.data.update(attrs)
        for key in childs.keys():
            childs[key] = childs[key][0]
        self.data.update(childs)


LabelInfoList = list_factory("LabelInfoList", LabelInfo, "label-info")


class NameCredit(UserDict):
    mapping = {
        "artist": Artist,
        "name": parse_str,
    }

    def __init__(self, attrs, childs, data):
        super().__init__()
        self.data.update(attrs)
        for key in childs.keys():
            childs[key] = childs[key][0]
        self.data.update(childs)


ArtistCredit = list_factory("ArtistCredit", NameCredit, "name-credit")


class Track(UserDict):
    mapping = {
        "artist-credit": ArtistCredit,
        "length": parse_int,
        "number": parse_str,
        "position": parse_int,
        "recording": Recording,
        "title": parse_str,
    }

    def __init__(self, attrs, childs, data):
        super().__init__()
        self.data.update(attrs)
        for key in childs.keys():
            childs[key] = childs[key][0]
        self.data.update(childs)


TrackList = list_factory("TrackList", Track, "track")


class Disc(UserDict):
    mapping = {
        "offset-list": OffsetList,
        "release-list": ReleaseList,
        "sectors": parse_int,
    }

    def __init__(self, attrs, childs, data):
        super().__init__()
        self.data.update(attrs)
        for key in childs.keys():
            childs[key] = childs[key][0]
        self.data.update(childs)


DiscList = list_factory("DiscList", Disc, "disc")


class Medium(UserDict):
    mapping = {
        "title": parse_str,
        "position": parse_int,
        "format": Format,
        "disc-list": DiscList,
        "pregap": Track,
        "track-list": TrackList,
        "data-track-list": TrackList,
    }

    def __init__(self, attrs, childs, data):
        super().__init__()
        self.data.update(attrs)
        for key in childs.keys():
            childs[key] = childs[key][0]
        self.data.update(childs)


MediumList = list_factory("MediumList", Medium, "medium")


class Annotation(UserDict):
    mapping = {
        "entity": parse_str,
        "name": parse_str,
        "text": parse_str,
    }

    def __init__(self, attrs, childs, data):
        super().__init__()
        self.data.update(attrs)
        for key in childs.keys():
            childs[key] = childs[key][0]
        self.data.update(childs)


AnnotationList = list_factory("AnnotationList", Annotation, "annotation")


class CDStubTrack(UserDict):
    mapping = {
        "artist": parse_str,
        "length": parse_int,
        "title": parse_str,
    }

    def __init__(self, attrs, childs, data):
        super().__init__()
        self.data.update(attrs)
        for key in childs.keys():
            childs[key] = childs[key][0]
        self.data.update(childs)


CDStubTrackList = list_factory("CDStubTrackList", CDStubTrack, "track")


class CDStub(UserDict):
    mapping = {
        "title": parse_str,
        "artist": parse_str,
        "barcode": parse_str,
        "disambiguation": parse_str,
        "track-list": CDStubTrackList,
    }

    def __init__(self, attrs, childs, data):
        super().__init__()
        self.data.update(attrs)
        for key in childs.keys():
            childs[key] = childs[key][0]
        self.data.update(childs)


CDStubList = list_factory("CDStubList", CDStub, "cdstub")


class LifeSpan(UserDict):
    mapping = {
        "begin": parse_str,
        "end": parse_str,
        "ended": parse_bool,
    }

    def __init__(self, attrs, childs, data):
        super().__init__()
        for key in childs.keys():
            childs[key] = childs[key][0]
        self.data.update(childs)


class TextRepresentation(UserDict):
    mapping = {
        "language": parse_str,
        "script": parse_str,
    }

    def __init__(self, attrs, childs, data):
        super().__init__()
        for key in childs.keys():
            childs[key] = childs[key][0]
        self.data.update(childs)


class Coordinates(UserDict):
    mapping = {
        "latitude": parse_str,
        "longitude": parse_str,
    }

    def __init__(self, attrs, childs, data):
        super().__init__()
        for key in childs.keys():
            childs[key] = childs[key][0]
        self.data.update(childs)


class ReleaseEvent(UserDict):
    mapping = {
        "date": parse_str,
        "area": Area,
    }

    def __init__(self, attrs, childs, data):
        super().__init__()
        self.data.update(attrs)
        for key in childs.keys():
            childs[key] = childs[key][0]
        self.data.update(childs)


ReleaseEventList = list_factory(
    "ReleaseEventList", ReleaseEvent, "release-event"
)


class PUID(UserDict):
    mapping = {
        "recording-list": RecordingList,
    }

    def __init__(self, attrs, childs, data):
        super().__init__()
        self.data.update(attrs)
        for key in childs.keys():
            childs[key] = childs[key][0]
        self.data.update(childs)


PUIDList = list_factory("PUIDList", PUID, "puid")


class ISRC(UserDict):
    mapping = {
        "recording-list": RecordingList,
    }

    def __init__(self, attrs, childs, data):
        super().__init__()
        self.data.update(attrs)
        for key in childs.keys():
            childs[key] = childs[key][0]
        self.data.update(childs)


ISRCList = list_factory("ISRCList", ISRC, "isrc")


class CoverArtArchive(UserDict):
    mapping = {
        "artwork": parse_bool,
        "back": parse_bool,
        "count": parse_int,
        "darkened": parse_bool,
        "front": parse_bool,
    }

    def __init__(self, attrs, childs, data):
        super().__init__()
        self.data.update(attrs)
        for key in childs.keys():
            childs[key] = childs[key][0]
        self.data.update(childs)


class Relation(UserDict):
    mapping = {
        "area": Area,
        "artist": Artist,
        "attribute-list": RelationAttributeList,
        "begin": parse_str,
        "direction": parse_direction,
        "end": parse_str,
        "ended": parse_bool,
        "event": Event,
        "instrument": Instrument,
        "label": Label,
        "ordering-key": parse_int,
        "place": Place,
        "recording": Recording,
        "release": Release,
        "release-group": ReleaseGroup,
        "series": Series,
        "source-credit": parse_str,
        "target": parse_str,
        "target-credit": parse_str,
        "work": Work,
    }

    def __init__(self, attrs, childs, data):
        super().__init__()
        self.data.update(attrs)
        for key in childs.keys():
            childs[key] = childs[key][0]
        self.data.update(childs)


RelationList = list_factory("RelationList", Relation, "relation")


class Metadata(UserDict):
    mapping = {
        "annotation-list": AnnotationList,
        "area": Area,
        "area-list": AreaList,
        "artist": Artist,
        "artist-list": ArtistList,
        "cdstub": CDStub,
        "cdstub-list": CDStubList,
        "collection": Collection,
        "collection-list": CollectionList,
        "disc": Disc,
        "event": Event,
        "event-list": EventList,
        "genre": Genre,
        "genre-list": GenreList,
        "instrument": Instrument,
        "instrument-list": InstrumentList,
        "isrc": ISRC,
        "isrc-list": ISRCList,
        "label": Label,
        "label-list": LabelList,
        "place": Place,
        "place-list": PlaceList,
        "puid": PUID,
        "rating": Rating,
        "recording": Recording,
        "recording-list": RecordingList,
        "release": Release,
        "release-group": ReleaseGroup,
        "release-group-list": ReleaseGroupList,
        "release-list": ReleaseList,
        "series": Series,
        "series-list": SeriesList,
        "tag-list": TagList,
        "url": Url,
        "url-list": UrlList,
        "user-genre-list": GenreList,
        "user-rating": parse_int,
        "user-tag-list": TagList,
        "work": Work,
        "work-list": WorkList,
    }

    @staticmethod
    def parse_date(data):
        if isinstance(data, str):
            return datetime.datetime.strptime(data, "%Y-%m-%dT%H:%M:%S")
        return data

    def __init__(self, attrs, childs, data):
        super().__init__()
        self.data.update(attrs)
        for key in childs.keys():
            childs[key] = childs[key][0]
        self.data.update(childs)
        if hasattr(self, "created"):
            self.created = self.parse_date(self.created)


class Root(UserDict):
    mapping = {"metadata": Metadata}

    def __init__(self, metadata):
        super().__init__()
        self.matadata = metadata


class Parser(object):
    StackElement = namedtuple(
        "StackElement", ("cls", "attrs", "childs", "data")
    )

    def __init__(self):
        self.stack = [self.StackElement(Root, {}, defaultdict(list), None)]

    @staticmethod
    def _normalize(tag):
        return tag.replace("{http://musicbrainz.org/ns/mmd-2.0#}", "")

    def start(self, tag, attrs):
        tag = self._normalize(tag)
        cls = self.stack[-1].cls
        try:
            new_cls = cls.mapping[tag]
        except IndexError:
            raise ValueError("unexcepted tag {tag}")

        self.stack.append(
            self.StackElement(new_cls, attrs, defaultdict(list), None)
        )

    def end(self, tag):
        tag = self._normalize(tag)
        cls, attrs, childs, data = self.stack.pop(-1)
        obj = cls(attrs, childs, data)
        self.stack[-1].childs[tag].append(obj)

    def data(self, data):
        self.stack[-1] = self.stack[-1]._replace(data=data)

    def close(self):
        if len(self.stack) != 1:
            raise ValueError("excepted one root")
        return self.stack[-1].childs["metadata"][0]


for cls in (
    Area,
    Artist,
    Collection,
    Event,
    Instrument,
    Label,
    Place,
    Recording,
    ReleaseGroup,
    Release,
    Series,
    Url,
    Work,
):
    cls.init()
