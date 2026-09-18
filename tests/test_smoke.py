"""冒烟测试：确认项目包结构可正常导入。"""


def test_core_packages_importable() -> None:
    import agent
    import servers
    from servers import lme_price, mineral_pdf, mining_news

    assert agent and servers
    assert lme_price and mineral_pdf and mining_news
