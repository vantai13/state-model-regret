"""Doan Van Tai — finite-domain membership and forbidden-feature independence."""
import json

from experiments.A03_card.membership import GRID_PATH, all_memberships, coordinates


def test_membership_from_coordinates_only():
    r = all_memberships()
    assert r['K5_list'] == r['K5_k3'] == {'main': ['M19', 'M20', 'M21', 'M22'], 'heldout': []}
    assert r['K5_kge2'] == {'main': ['M19', 'M20', 'M21', 'M22'], 'heldout': ['R03', 'R04']}
    assert r['P2_optional'] == {'main': ['M09', 'M10', 'M11', 'M12'], 'heldout': ['R07', 'R08']}
    assert r['P3_optional'] == {'main': ['M19', 'M21'], 'heldout': ['R03']}
    assert set(coordinates()[0]) == {'id', 'section', 'kappa', 'alphaA', 'alphaB', 'eta', 'h', 'targets', 'candidate'}


def test_forbidden_features_do_not_change_membership(tmp_path):
    g = json.loads(GRID_PATH.read_text())
    for section in ('main', 'heldout'):
        for row in g[section]:
            # Poison every actual sign probability and load value, leaving targets intact.
            row['lambdaA'] = 'must-not-be-parsed'
            row['psi'] = row['delta'] = 'must-not-be-parsed'
            for key in list(row):
                if key.startswith(('p_', 'unresolved_', 'updates_', 'peak_')):
                    row[key] = 'must-not-be-parsed'
            for a in row['anchors']:
                a['lambdaA'] = a['p_coarse'] = 'must-not-be-parsed'
    path = tmp_path / 'poisoned.json'
    path.write_text(json.dumps(g))
    assert all_memberships(path) == all_memberships()
