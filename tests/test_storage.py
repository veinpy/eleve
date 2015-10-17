import pytest
import re

from eleve import PyMemoryStorage

from utils import float_equal, compare_node
from conftest import all_storage, all_storage_nocreate, tested_storage, storage_name


@pytest.mark.parametrize("storage", all_storage, indirect=True, ids=storage_name)
def test_basic(storage):
    """
    Forward that begins by « le petit »:
     - le petit chat
     - le petit chien
     - le petit $ * 2
    Backward that begins by « petit le » :
     - petit le ^ * 2
     - petit le pour * 2
    --> count is the mean of 4 and 4, and entropy is the mean of 2 (the None are counted separately) and 1.5.
    """
    storage.clear()

    storage.add_sentence(['le','petit','chat'])
    storage.add_sentence(['le','petit','chien'])
    storage.add_sentence(['pour','le','petit'], freq=2)

    assert float_equal(storage.query_count(['le', 'petit']), 4.0)
    assert float_equal(storage.query_count(['pour']), 2.0)
    assert float_equal(storage.query_entropy(['le', 'petit']), 1.75)
    assert float_equal(storage.query_autonomy(['le', 'petit']),1.89582)


@pytest.mark.parametrize("storage", all_storage_nocreate, indirect=True, ids=storage_name)
def test_ngram_length(storage):
    # the default value should be is 5
    assert storage.default_ngram_length == 5
    # this default value should be used in add_sentence
    storage.add_sentence("un petit petit petit chat danse la samba".split())
    assert float_equal(storage.query_count('un petit petit petit chat'.split()), 1.0)
    assert float_equal(storage.query_count('un petit petit petit chat danse'.split()), 0.0)
    # but this default value may be overriden in add_sentence
    storage.add_sentence("it is very very very cool".split(), ngram_length=2)
    assert float_equal(storage.query_count('very cool'.split()), 1.0)
    assert float_equal(storage.query_count('very very cool'.split()), 0.0)

    # if leveldb
    storage_class = storage.__class__
    if "Leveldb" in storage_class.__name__: #XXX: ajout méthode (backend() qui retourne une constant fct du type de backend)
        storage_path  = storage.path
        storage.close()
        del storage
        reopened_storage = storage_class(storage_path)
        assert reopened_storage.default_ngram_length == 5


@pytest.mark.parametrize("storage", all_storage_nocreate, indirect=True, ids=storage_name)
def test_clear(storage):
    assert float_equal(storage.query_count('le'.split()), 0.0)
    storage.clear()
    storage.add_sentence('le petit chat'.split())
    storage.add_sentence('le gros chien'.split())
    assert float_equal(storage.query_count('le'.split()), 2.0)
    assert float_equal(storage.query_count('le petit'.split()), 1.0)
    storage.clear()
    assert float_equal(storage.query_count('le'.split()), 0.0)
    assert float_equal(storage.query_count('le petit'.split()), 0.0)
    storage.add_sentence('le sac jaune'.split())
    storage.add_sentence('le sac rouge'.split(), freq=3)
    assert float_equal(storage.query_count('le'.split()), 4.0)
    assert float_equal(storage.query_count('sac rouge'.split()), 3.0)


@pytest.mark.parametrize("storage", all_storage_nocreate, indirect=True, ids=storage_name)
def test_add_negativ_freq(storage):
    storage.clear()
    storage.add_sentence('le petit chat'.split())
    storage.add_sentence('un chat vert et violet'.split())
    storage.add_sentence('un chien vert et violet'.split())
    storage.add_sentence('le gros chien'.split())
    assert float_equal(storage.query_count('le'.split()), 2.0)
    assert float_equal(storage.query_count('le petit'.split()), 1.0)
    storage.add_sentence('le petit chat'.split(), freq=-1)
    assert float_equal(storage.query_count('le'.split()), 1.0)
    assert float_equal(storage.query_count('le petit'.split()), 0.0)
    
    # remove unexisting sentence
    storage.add_sentence('pas cool'.split(), freq=-5)
    assert float_equal(storage.query_count('pas cool'.split()), 0.0)

    assert float_equal(storage.query_count('vert et violet'.split()), 2.0)
    storage.add_sentence('le gros chien vert et violet'.split(), freq=-2)
    assert float_equal(storage.query_count('vert et violet'.split()), 0.0)


@pytest.mark.parametrize("storage", tested_storage, indirect=['storage'])
def test_storage(ngram_length, storage, ref_class=PyMemoryStorage):
    ref = ref_class(default_ngram_length=ngram_length)
    ref.clear()
    storage.clear()

    testfile = open('tests/fixtures/btree.txt').read().split('\n')
    sentences = (re.findall(r'\w+', sentence) for sentence in testfile)
    for sentence in sentences:
        ref.add_sentence(sentence, ngram_length=ngram_length)
        storage.add_sentence(sentence, ngram_length=ngram_length)

    # compare of each ngram of each sentence
    for sentence in sentences:
        for start in range(len(sentence)):
            for length in range(ngram_length):
                ngram = sentence[start:start+length]
                compare_node(ngram, ref, storage)


