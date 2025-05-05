import re


class TokenError(Exception):
    pass


class Token(object):
    pass


class FullRenameToken(object):
    consumes = 1

    def __init__(self, rename_str):
        self.rename_str = rename_str

    def __call__(self, in_str):
        return self.rename_str

    @staticmethod
    def match(part):
        if part.startswith("-"):
            return False
        invalid_chars = "!@$%^&*()[]\\|;,<.?/+="
        return all(c not in part for c in invalid_chars)


class SubstituteToken(Token):
    consumes = 2

    def __init__(self, search_str, replace_str):
        self.search_str = search_str
        self.replace_str = replace_str

    def __call__(self, in_str):
        return in_str.replace(self.search_str, self.replace_str)

    @staticmethod
    def match(part, next_part):
        if part.startswith("+") or next_part.startswith("+"):
            return False
        if part.endswith("+") or next_part.endswith("+"):
            return False
        if part.startswith("-") or next_part.startswith("-"):
            return False
        return True


class RemoveToken(Token):
    consumes = 1

    def __init__(self, remove_str):
        self.remove_str = remove_str.lstrip("-")

    def __call__(self, in_str):
        return in_str.replace(self.remove_str, "")

    @staticmethod
    def match(part):
        return part.startswith("-")


class AddSuffixToken(Token):
    consumes = 1

    def __init__(self, add_str):
        self.add_str = add_str.lstrip("+")

    def __call__(self, in_str):
        return in_str + self.add_str

    @staticmethod
    def match(part):
        return part.startswith("+")


class AddPrefixToken(Token):
    consumes = 1

    def __init__(self, add_str):
        self.add_str = add_str.rstrip("+")

    def __call__(self, in_str):
        return self.add_str + in_str

    @staticmethod
    def match(part):
        return part.endswith("+")


def preprocess_string(rename_str):
    """Preprocesses rename_str and extracts arguments for formatting."""

    format_args = []
    matches = re.findall(r"(#+)(\((\d+)\))?", rename_str)
    for i, match in enumerate(matches):
        padding = len(match[0])
        start = 1
        if match[2]:
            start = int(match[2])
        rename_str = re.sub(
            re.escape(match[0] + match[1]), "{%d:0>%d}" % (i, padding), rename_str, 1
        )
        format_args.append(start)
    return rename_str, format_args


class Renamer(object):
    def __init__(self, rename_str):
        self.original_str = rename_str
        self.rename_str, self.start_values = preprocess_string(rename_str)
        self.tokens = []
        self.tokenize()

    def tokenize(self):
        parts = self.rename_str.split()

        if len(parts) == 1 and FullRenameToken.match(parts[0]):
            self.tokens.append(FullRenameToken(parts[0]))
            return

        while parts:
            num_parts = len(parts)

            for token in Token.__subclasses__():
                if len(parts) < token.consumes:
                    continue

                match_parts = parts[: token.consumes]
                if token.match(*match_parts):
                    self.tokens.append(token(*match_parts))
                    for _ in range(token.consumes):
                        parts.pop(0)

            if num_parts == len(parts):
                self.tokens = []
                raise TokenError(parts[0] + " is not a valid string")

    def rename(self, input_str, index=None):
        if not self.tokens:
            self.tokenize()

        for token in self.tokens:
            input_str = token(input_str)

        if self.start_values and index is not None:
            indices = [v + index for v in self.start_values]
            input_str = input_str.format(*indices)

        return input_str
