import sys
import os

sys.path.append(os.path.abspath(os.path.dirname(__file__) + os.sep + os.pardir))
import edit_db


def test_get_repo_id():
    assert edit_db.get_repo_id('alpine') == dict(publisher='library', repo_name='alpine', repo_tag='latest')
    assert edit_db.get_repo_id('alpine:latest') == dict(publisher='library', repo_name='alpine', repo_tag='latest')
    assert edit_db.get_repo_id('alpine:3.10') == dict(publisher='library', repo_name='alpine', repo_tag='3.10')
    assert edit_db.get_repo_id('library/alpine') == dict(publisher='library', repo_name='alpine', repo_tag='latest')
    assert edit_db.get_repo_id('library/alpine:latest') == dict(publisher='library', repo_name='alpine', repo_tag='latest')
    assert edit_db.get_repo_id('library/alpine:3.10') == dict(publisher='library', repo_name='alpine', repo_tag='3.10')

    assert edit_db.get_repo_id('gitlab/gitlab-ce') == dict(publisher='gitlab', repo_name='gitlab-ce', repo_tag='latest')
    assert edit_db.get_repo_id('gitlab/gitlab-ce:latest') == dict(publisher='gitlab', repo_name='gitlab-ce', repo_tag='latest')
    assert edit_db.get_repo_id('gitlab/gitlab-ce:12.6.4-ce.0') == dict(publisher='gitlab', repo_name='gitlab-ce', repo_tag='12.6.4-ce.0')

    assert edit_db.get_repo_id('') is None
    assert edit_db.get_repo_id(None) is None
    assert edit_db.get_repo_id(1) is None
