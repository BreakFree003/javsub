from engine.translate import parse_response


def test_parse_basic():
    text = """#1
Translation>
何してるの？在干嘛？

#2
Translation>
見てないよ没看
"""
    trans, summary, scene = parse_response(text)
    assert trans[1] == "何してるの？在干嘛？"
    assert trans[2] == "見てないよ没看"
    assert summary == ""
    assert scene == ""


def test_parse_with_tags():
    text = """<summary>
房间里
</summary>
<scene>
对话场景
</scene>
#1
Translation>
在干嘛？
"""
    trans, summary, scene = parse_response(text)
    assert summary == "房间里"
    assert scene == "对话场景"
    assert trans[1] == "在干嘛？"


def test_parse_yiwen_prefix():
    text = """#1
译文>
在干嘛？
"""
    trans, summary, scene = parse_response(text)
    assert trans[1] == "在干嘛？"


def test_parse_multiline():
    text = """#1
Translation>
第一行
第二行
#2
Translation>
单行
"""
    trans, summary, scene = parse_response(text)
    assert trans[1] == "第一行\n第二行"
    assert trans[2] == "单行"


def test_parse_empty():
    assert parse_response("") == ({}, "", "")
    assert parse_response("  ") == ({}, "", "")


def test_parse_missing_translation_marker():
    text = """#1
Translation>
译文1
#2
译文2
"""
    trans, summary, scene = parse_response(text)
    assert trans[1] == "译文1"
    assert trans[2] == "译文2"


def test_parse_number_only_no_translation():
    text = """#1
#2
Translation>
译文2
"""
    trans, summary, scene = parse_response(text)
    assert trans[2] == "译文2"
    assert 1 not in trans
