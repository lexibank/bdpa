def test_valid(cldf_dataset, cldf_logger):
    assert cldf_dataset.validate(log=cldf_logger)


def test_forms(cldf_dataset):
    assert len(list(cldf_dataset["FormTable"])) == 50095
    assert any(f["Form"] == "sɛ̃⁵⁵tsɿ³³tɯ²¹" for f in cldf_dataset["FormTable"])


def test_parameters(cldf_dataset):
    assert len(list(cldf_dataset["ParameterTable"])) == 590


def test_languages(cldf_dataset):
    assert len(list(cldf_dataset["LanguageTable"])) == 538
