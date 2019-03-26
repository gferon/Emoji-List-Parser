from emoji_parser import Emoji, Status, SkinTone, Group
from fontTools.ttLib import TTFont
import os

class GenCSharp:

    def __init__(self, fontPath: str, srcUrl: str):
        self.font = TTFont(fontPath)
        self.srcUrl = srcUrl

    def __genCamelCaseName(self, emoji: Emoji) -> str:
        return "".join([s.capitalize() for s in emoji.searchTerms if s.isalnum()])

    def __genSearchTerms(self, emoji: Emoji) -> str:
        return "\"" + "\", \"".join(emoji.searchTerms) + "\""

    def __genSkinTones(self, emoji: Emoji) -> str:
        return "SkinTone." + ", SkinTone.".join([tone.name for tone in emoji.skinTones])

    def __genGroup(self, emoji: Emoji) -> str:
        return "SkinTone." + ", SkinTone.".join([tone.name for tone in emoji.skinTones])

    def __genMachinegeneratedHeader(self) -> str:
        return ("\t// This file is machine-generated based on the official Unicode Consortium publication (" + self.srcUrl + ").\n"
            "\t// See https://github.com/UWPX/Emoji-List-Parser for the generator.\n")

    def genEmojiString(self, emoji: Emoji):
        return ("\t\tpublic static readonly SingleEmoji " + self.__genCamelCaseName(emoji) + " = new SingleEmoji(\n"
            "\t\t\tsequence: new UnicodeSequence(\"" + emoji.codePoint + "\"),\n"
            "\t\t\tname: \"" + emoji.name + "\",\n"
            "\t\t\tsearchTerms: new[] { " + self.__genSearchTerms(emoji) + " },\n"
            "\t\t\tskinTones: new[] { " + self.__genSkinTones(emoji) + " },\n"
            "\t\t\tgroup: Group." + emoji.group.name + ",\n"
            "\t\t\tsubgroup: \"" + emoji.subgroup + "\",\n"
            "\t\t\thasGlyph: " + str(self.__isEmojiSupportedByFont(emoji)).lower() + ",\n"
            "\t\t\tsortOrder: " + str(emoji.index) + "\n"
            "\t\t);\n")

    def genEmojiDeclarationsFile(self, emoji: list):
        if not os.path.exists("out"):
            os.makedirs("out")
        outFile = open("out/Emoji-Emojis.cs", "w", encoding="utf-8")

        output = ("namespace NeoSmart.Unicode\n"
            "{\n"
            + self.__genMachinegeneratedHeader()
            + "\tpublic static partial class Emoji\n"
            "\t{\n")

        for e in emoji:
            if e.status == Status.COMPONENT or e.status == Status.FULLY_QUALIFIED:
                output += self.genEmojiString(e)

        output += "\t}\n}\n"
        outFile.write(output)
        outFile.close()

    def genEmojiAllFile(self, emoji: list):
        if not os.path.exists("out"):
            os.makedirs("out")
        outFile = open("out/Emoji-All.cs", "w", encoding="utf-8")

        output = ("using System.Collections.Generic;\n"
            "\n"
            "namespace NeoSmart.Unicode\n"
            "{\n"
            + self.__genMachinegeneratedHeader()
            + "\tpublic static partial class Emoji\n"
            "\t{\n"
            "\t\t/// <summary>\n"
            "\t\t/// A (sorted) enumeration of all emoji.\n"
            "\t\t/// Only contains fully-qualified and component emoji.\n"
            "\t\t/// <summary>\n")
        output += self.__genSingleEmojiStart("All")

        for e in emoji:
            if e.status == Status.COMPONENT or e.status == Status.FULLY_QUALIFIED:
                output += "\t\t\t/* " + e.emoji + " */ " + self.__genCamelCaseName(e) + ",\n"

        output += "\t\t};\n\t}\n}\n"
        outFile.write(output)
        outFile.close()

    def genEmojiGroupFile(self, emoji: list, group: Group):
        if not os.path.exists("out"):
            os.makedirs("out")

        groupName = "".join([s.lower().capitalize() for s in group.name.split("_")])
        outFile = open("out/Emoji-" + groupName + ".cs", "w", encoding="utf-8")

        output = ("using System.Collections.Generic;\n"
            "\n"
            "namespace NeoSmart.Unicode\n"
            "{\n"
            + self.__genMachinegeneratedHeader()
            + "\tpublic static partial class Emoji\n"
            "\t{\n"
            "\t\t/// <summary>\n"
            "\t\t/// A (sorted) enumeration of all emoji in group: " + group.name + "\n"
            "\t\t/// Only contains fully-qualified and component emoji.\n"
            "\t\t/// <summary>\n")
        output += self.__genSingleEmojiStart(groupName)

        for e in emoji:
            if (e.status == Status.COMPONENT or e.status == Status.FULLY_QUALIFIED) and e.group == group:
                output += "\t\t\t/* " + e.emoji + " */ " + self.__genCamelCaseName(e) + ",\n"

        output += "\t\t};\n\t}\n}\n"
        outFile.write(output)
        outFile.close()

    def __isEmojiSupportedByFont(self, emoji: Emoji):
        code = sum([ord(i) for i in emoji.emoji])
        for table in self.font['cmap'].tables:
            for char_code, glyph_name in table.cmap.items():
                if char_code == code:
                    return True
        return False
    
    def __genSingleEmojiStart(self, name: str):
        return ("#if NET20 || NET30 || NET35\n"
            "\t\tpublic static readonly List<SingleEmoji> " + name + " = new List<SingleEmoji>() {\n"
            "#else\n"
            "\t\tpublic static SortedSet<SingleEmoji> " + name + " => new SortedSet<SingleEmoji>() {\n"
            "#endif\n")

    def genEmojiBasicFile(self, emoji: list):
        if not os.path.exists("out"):
            os.makedirs("out")
        outFile = open("out/Emoji-Basic.cs", "w", encoding="utf-8")

        output = ("using System.Collections.Generic;\n"
            "\n"
            "namespace NeoSmart.Unicode\n"
            "{\n"
            + self.__genMachinegeneratedHeader()
            + "\tpublic static partial class Emoji\n"
            "\t{\n"
            "\t\t/// <summary>\n"
            "\t\t/// A (sorted) enumeration of all emoji without skin variations and no duplicate gendered vs gender-neutral emoji, ideal for displaying.\n"
            "\t\t/// Emoji without supported glyphs in Segoe UI Emoji are also omitted from this list.\n"
            "\t\t/// <summary>\n")
        output += self.__genSingleEmojiStart("Basic")

        # The path to the Segoe UI Emoji font file under Windows 10:
        for e in emoji:
            if (e.status == Status.COMPONENT or e.status == Status.FULLY_QUALIFIED) and SkinTone.NONE in e.skinTones and self.__isEmojiSupportedByFont(e):
                output += "\t\t\t/* " + e.emoji + " */ " + self.__genCamelCaseName(e) + ",\n"

        output += "\t\t};\n\t}\n}\n"
        outFile.write(output)
        outFile.close()

    def gen(self, emoji: list):
        # Emoji-Emojis.cs
        self.genEmojiDeclarationsFile(emoji)
        # Emoji-All.cs
        self.genEmojiAllFile(emoji)
        # Emoji-Basic.cs
        self.genEmojiBasicFile(emoji)

        # Emoji-SmileysAndEmotion.cs
        self.genEmojiGroupFile(emoji, Group.SMILEYS_AND_EMOTION)
        # Emoji-PeopleAndBody.cs
        self.genEmojiGroupFile(emoji, Group.PEOPLE_AND_BODY)
        # Emoji-Component.cs
        self.genEmojiGroupFile(emoji, Group.COMPONENT)
        # Emoji-AnimalsAndNature.cs
        self.genEmojiGroupFile(emoji, Group.ANIMALS_AND_NATURE)
        # Emoji-FoodAndDrink.cs
        self.genEmojiGroupFile(emoji, Group.FOOD_AND_DRINK)
        # Emoji-TravelAndPlaces.cs
        self.genEmojiGroupFile(emoji, Group.TRAVEL_AND_PLACES)
        # Emoji-Activities.cs
        self.genEmojiGroupFile(emoji, Group.ACTIVITIES)
        # Emoji-Objects.cs
        self.genEmojiGroupFile(emoji, Group.OBJECTS)
        # Emoji-Symbols.cs
        self.genEmojiGroupFile(emoji, Group.SYMBOLS)
        # Emoji-Flags.cs
        self.genEmojiGroupFile(emoji, Group.FLAGS)

        