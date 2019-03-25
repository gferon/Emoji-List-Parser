from enum import Enum
import requests
import re

class SkinTone(Enum):
    NONE = 0
    LIGHT = 1
    MEDIUM_LIGHT = 2
    MEDIUM = 3
    MEDIUM_DARK = 4
    DARK = 5

class Status(Enum):
    COMPONENT = 0
    FULLY_QUALIFIED = 1
    MINIMALLY_QUALIFIED = 2
    UNQUALIFIED = 3

class Emoji:
    """
    A representation for an unicode emoji.

    ...

    Attributes
    ----------
    codePoint : str
        list of one or more hex code points, separated by spaces e.g. "1F600" or "1F468 1F3FF 200D 2695 FE0F"
    emoji : str
        the actual emoji e.g. "😀" or "👨🏿‍⚕️"
    name : str
        the actual name of the emoji e.g. "grinning face" or "man health worker: dark skin tone"

    searchTerms : list
        a list of string search terms that describe the emoji e.g. ["grinning", "face"] or ["man", "health", "worker", "dark", "skin", "tone"]

    skinTones : list
        a list of SkinTone objects for the emoji e.g. [SkinTone.NONE] for "😀" , [SkinTone.DARK] for "👨🏿‍⚕️" and [SkinTone.DARK, SkinTone.MEDIUM] for "🧑🏿‍🤝‍🧑🏽"

    status : Status
        the status of the emoji e.g. Status.FULLY_QUALIFIED for "😀" and Status.COMPONENT for "🏻"

    group : str
        the group the emoji is part of e.g. "Smileys & Emotion" or "People & Body"

    subgroup : str
        the subgroup the emoji is part of e.g. "face-smiling" or "person-role"

    index : int
        the index of the emoji in the emoji-test.txt list
    """

    def __init__(self, codePoint: str, emoji: str, name: str, searchTerms: list, skinTones: list, status: Status, group: str, subgroup: str, index: int):
        self.codePoint = codePoint
        self.emoji = emoji
        self.name = name
        self.searchTerms = searchTerms
        self.skinTones = skinTones
        self.status = status
        self.group = group
        self.subgroup = subgroup
        self.index = index

class EmojiParser:
    """
    A class used to represent an Animal

    ...

    Attributes
    ----------
    url : str
        the url for where we should get the "emoji-test.txt" from

    Methods
    -------
    parse(url: str)
        downloads the emoji file specified in url and returns a list of Emoji objects or None if the download failed
    """

    def __init__(self, url: str):
        self.url = url

    def parse(self) -> list:
        """
        Downloads the emoji file specified in url and returns a list of Emoji objects or None if the download failed.

        Returns
        -------
        list
            a list of Emoji objects if the download was successfull else None
        """
        text = self.__downloadList()
        if text is None:
            return None
        
        lines = text.splitlines()
        lines = self.__removeNotImpLines(lines)

        emoji = []
        group = ""
        subgroup = ""
        index = 0
        for l in lines:
            if l.startswith("# group:"):
                group = self.__parseGroup(l)
            elif l.startswith("# subgroup:"):
                subgroup = self.__parseSubgroup(l)
            elif not l.startswith("#"):
                e = self.__parseEmoji(l, group, subgroup, index)
                if e:
                    emoji.append(e)
                    index += 1

        return emoji

    def __downloadList(self) -> str: 
        resp = requests.get(self.url)
        return resp.text

    def __removeNotImpLines(self, lines: list) -> list:
        # Remove start comment:
        result = []
        for l in lines:
            if not l.startswith("#") or l.startswith("# group:") or l.startswith("# subgroup:"):
                result.append(l)

        # Remove empty lines:
        return [l for l in result if l]

    def __parseGroup(self, s: str) -> str:
        return s.replace("# group: ", "").strip()

    def __parseSubgroup(self, s: str) -> str:
        return s.replace("# subgroup: ", "").strip()

    def __parseEmoji(self, s: str, group: str, subgroup: str, index: int) -> Emoji:
        parts = s.split(";")
        if len(parts) != 2:
            print("Invalid line for parsing emoji part 1:" + s)
            return None

        # Code point:
        codePoint = parts[0].strip()

        # Special case for the 'keycap' subgroup:
        endWithSeperator = s.strip().endswith('#')

        parts = parts[1].split("#")
        parts = [l for l in parts if l and l.strip()]
        if len(parts) != 2:
            print("Invalid line for parsing emoji part 2:" + s)
            return None

        if endWithSeperator:
            parts[1] = parts[1] + "#"
        
        # Status:
        statusS = parts[0].strip()
        status = Status.COMPONENT

        if statusS == "component":
            status = Status.COMPONENT
        elif statusS == "fully-qualified":
            status = Status.FULLY_QUALIFIED
        elif statusS == "minimally-qualified":
            status = Status.MINIMALLY_QUALIFIED
        elif statusS == "unqualified":
            status = Status.UNQUALIFIED
        else:
            print("Unknown status found: " + statusS)

        parts = parts[1].strip().split()

        if len(parts) < 2:
            print("Invalid line for parsing emoji part 3:" + s)
            return None

        # Emoji:
        emoji = parts[0]
        del parts[0]

        # Name:
        name = " ".join(parts)

        # Skin tone:
        skinTonesS = codePoint
        skinTones = []
        found = True

        while found:
            found = False
            # 🏻 light skin tone:
            if "1F3FB" in skinTonesS:
                skinTonesS = skinTonesS.replace("1F3FB", "")
                skinTones.append(SkinTone.LIGHT)
                found = True
            # 🏼 medium-light skin tone:
            elif "1F3FC" in skinTonesS:
                skinTonesS = skinTonesS.replace("1F3FC", "")
                skinTones.append(SkinTone.MEDIUM_LIGHT)
                found = True
            # 🏽 medium skin tone:
            elif "1F3FD" in skinTonesS:
                skinTonesS = skinTonesS.replace("1F3FD", "")
                skinTones.append(SkinTone.MEDIUM)
                found = True
            # 🏾 medium-dark skin tone:
            elif "1F3FE" in skinTonesS:
                skinTonesS = skinTonesS.replace("1F3FE", "")
                skinTones.append(SkinTone.MEDIUM_DARK)
                found = True
            # 🏿 dark skin tone:
            elif "1F3FF" in skinTonesS:
                skinTonesS = skinTonesS.replace("1F3FF", "")
                skinTones.append(SkinTone.DARK)
                found = True

        # Default to no skin color aka. yellow:
        if len(skinTones) <= 0:
            skinTones.append(SkinTone.NONE)

        # Search terms:
        # Based on: https://github.com/neosmart/unicode.net/blob/3b0bd1867c96221b344084d8d82278f7c6a812b8/importers/emoji-importer.html#L13
        searchTermsS = re.sub(r"[,.'’“”!():]", "", name)
        searchTermsS = searchTermsS.replace("-", " ") \
            .replace("1st", "First") \
            .replace("2nd", "Second") \
            .replace("3rd", "Third") \
            .replace("#", "Hash") \
            .replace("*", "Asterisk")

        searchTerms = searchTermsS.split()

        # Based on: https://github.com/neosmart/unicode.net/blob/3b0bd1867c96221b344084d8d82278f7c6a812b8/importers/emoji-importer.html#L45
        unwanted =  ["of", "with", "without", "and", "or", "&", "-", "on", "the", "in"]
        searchTerms = [l.lower() for l in searchTerms if not (l in unwanted)]

        return Emoji(codePoint, emoji, name, searchTerms, skinTones, status, group, subgroup, index)