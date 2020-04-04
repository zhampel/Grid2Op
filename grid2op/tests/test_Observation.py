import os
import sys
import unittest
import datetime
import json
import warnings
from io import StringIO
import numpy as np
from numpy import dtype
import pdb

from grid2op.tests.helper_path_test import *

from grid2op.Exceptions import *
from grid2op.Observation import ObservationSpace, CompleteObservation, ObsEnv, BaseObservation
from grid2op.Chronics import ChronicsHandler, ChangeNothing, GridStateFromFile, GridStateFromFileWithForecasts
from grid2op.Action import ActionSpace
from grid2op.Rules import RulesChecker
from grid2op.Reward import L2RPNReward
from grid2op.Parameters import Parameters
from grid2op.Backend import PandaPowerBackend
from grid2op.Environment import Environment
from grid2op.MakeEnv import make

# TODO add unit test for the proper update the backend in the observation [for now there is a "data leakage" as
# the real backend is copied when the observation is built, but i need to make a test to check that's it's properly
# copied]


# temporary deactivation of all the failing test until simulate is fixed
DEACTIVATE_FAILING_TEST = True


class TestLoadingBackendFunc(unittest.TestCase):
    def setUp(self):
        """
        The case file is a representation of the case14 as found in the ieee14 powergrid.
        :return:
        """
        self.tolvect = 1e-2
        self.tol_one = 1e-5
        self.game_rules = RulesChecker()
        # pdb.set_trace()
        self.rewardClass = L2RPNReward
        self.reward_helper = self.rewardClass()
        self.obsClass = CompleteObservation
        self.parameters = Parameters()

        # powergrid
        self.backend = PandaPowerBackend()
        self.path_matpower = PATH_DATA_TEST_PP
        self.case_file = "test_case14.json"

        # chronics
        self.path_chron = os.path.join(PATH_CHRONICS, "chronics_with_forecast")
        self.chronics_handler = ChronicsHandler(chronicsClass=GridStateFromFileWithForecasts, path=self.path_chron)

        self.tolvect = 1e-2
        self.tol_one = 1e-5
        self.id_chron_to_back_load = np.array([0, 1, 10, 2, 3, 4, 5, 6, 7, 8, 9])

        # force the verbose backend
        self.backend.detailed_infos_for_cascading_failures = True

        self.names_chronics_to_backend = {"loads": {"2_C-10.61": 'load_1_0', "3_C151.15": 'load_2_1',
                                                    "14_C63.6": 'load_13_2', "4_C-9.47": 'load_3_3',
                                                    "5_C201.84": 'load_4_4',
                                                    "6_C-6.27": 'load_5_5', "9_C130.49": 'load_8_6',
                                                    "10_C228.66": 'load_9_7',
                                                    "11_C-138.89": 'load_10_8', "12_C-27.88": 'load_11_9',
                                                    "13_C-13.33": 'load_12_10'},
                                          "lines": {'1_2_1': '0_1_0', '1_5_2': '0_4_1', '9_10_16': '8_9_2',
                                                    '9_14_17': '8_13_3',
                                                    '10_11_18': '9_10_4', '12_13_19': '11_12_5', '13_14_20': '12_13_6',
                                                    '2_3_3': '1_2_7', '2_4_4': '1_3_8', '2_5_5': '1_4_9',
                                                    '3_4_6': '2_3_10',
                                                    '4_5_7': '3_4_11', '6_11_11': '5_10_12', '6_12_12': '5_11_13',
                                                    '6_13_13': '5_12_14', '4_7_8': '3_6_15', '4_9_9': '3_8_16',
                                                    '5_6_10': '4_5_17',
                                                    '7_8_14': '6_7_18', '7_9_15': '6_8_19'},
                                          "prods": {"1_G137.1": 'gen_0_4', "3_G36.31": "gen_2_1", "6_G63.29": "gen_5_2",
                                                    "2_G-56.47": "gen_1_0", "8_G40.43": "gen_7_3"},
                                          }

        # _parameters for the environment
        self.env_params = Parameters()

        self.env = Environment(init_grid_path=os.path.join(self.path_matpower, self.case_file),
                               backend=self.backend,
                               chronics_handler=self.chronics_handler,
                               parameters=self.env_params,
                               names_chronics_to_backend=self.names_chronics_to_backend,
                               rewardClass=self.rewardClass)

        self.dict_ = {'name_gen': ['gen_1_0', 'gen_2_1', 'gen_5_2', 'gen_7_3', 'gen_0_4'],
                      'name_load': ['load_1_0', 'load_2_1', 'load_13_2', 'load_3_3', 'load_4_4', 'load_5_5', 'load_8_6',
                                    'load_9_7', 'load_10_8', 'load_11_9', 'load_12_10'],
                      'name_line': ['0_1_0', '0_4_1', '8_9_2', '8_13_3', '9_10_4', '11_12_5', '12_13_6', '1_2_7',
                                    '1_3_8', '1_4_9', '2_3_10', '3_4_11', '5_10_12', '5_11_13', '5_12_14', '3_6_15',
                                    '3_8_16', '4_5_17', '6_7_18', '6_8_19'],
                      'name_sub': ['sub_0', 'sub_1', 'sub_10', 'sub_11', 'sub_12', 'sub_13', 'sub_2', 'sub_3', 'sub_4',
                                   'sub_5', 'sub_6', 'sub_7', 'sub_8', 'sub_9'],
                      'sub_info': [3, 6, 4, 6, 5, 6, 3, 2, 5, 3, 3, 3, 4, 3],
                      'load_to_subid': [1, 2, 13, 3, 4, 5, 8, 9, 10, 11, 12],
                      'gen_to_subid': [1, 2, 5, 7, 0],
                      'line_or_to_subid': [0, 0, 8, 8, 9, 11, 12, 1, 1, 1, 2, 3, 5, 5, 5, 3, 3, 4, 6, 6],
                      'line_ex_to_subid': [1, 4, 9, 13, 10, 12, 13, 2, 3, 4, 3, 4, 10, 11, 12, 6, 8, 5, 7, 8],
                      'load_to_sub_pos': [5, 3, 2, 5, 4, 5, 4, 2, 2, 2, 3], 'gen_to_sub_pos': [4, 2, 4, 1, 2],
                      'line_or_to_sub_pos': [0, 1, 0, 1, 1, 0, 1, 1, 2, 3, 1, 2, 0, 1, 2, 3, 4, 3, 1, 2],
                      'line_ex_to_sub_pos': [0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 2, 1, 1, 2, 0, 2, 3, 0, 3],
                      'load_pos_topo_vect': [8, 12, 55, 18, 23, 29, 39, 42, 45, 48, 52],
                      'gen_pos_topo_vect': [7, 11, 28, 34, 2],
                      'line_or_pos_topo_vect': [0, 1, 35, 36, 41, 46, 50, 4, 5, 6, 10, 15, 24, 25, 26, 16, 17, 22, 31,
                                                32],
                      'line_ex_pos_topo_vect': [3, 19, 40, 53, 43, 49, 54, 9, 13, 20, 14, 21, 44, 47, 51, 30, 37, 27,
                                                33, 38],
                      'gen_type': ['solar', 'nuclear', 'nuclear', 'nuclear', 'thermal'],
                      'gen_pmin': [0.0, 0.0, 0.0, 0.0, 0.0],
                      'gen_pmax': [50.0, 80.0, 120.0, 120.0, 190.0],
                      'gen_redispatchable': [False, True, True, True, True],
                      'gen_max_ramp_up': [50.0, 80.0, 120.0, 120.0, 190.0],
                      'gen_max_ramp_down': [50.0, 80.0, 120.0, 120.0, 190.0],
                      'gen_min_uptime': [0, 0, 0, 0, 0],
                      'gen_min_downtime': [0, 1, 0, 0, 0],
                      'gen_cost_per_MW': [0.0, 0.0, 0.0, 0.0, 10.0],
                      'gen_startup_cost': [0.0, 0.0, 0.0, 0.0, 0.0],
                      'gen_shutdown_cost': [0.0, 0.0, 0.0, 0.0, 0.0],
                      'subtype': 'grid2op.Observation.CompleteObservation.CompleteObservation',
                      "grid_layout": None,
                      'name_shunt': ['shunt_8_0'],
                      'shunt_to_subid': [8]}

        self.dtypes = np.array([dtype('int64'), dtype('int64'), dtype('int64'), dtype('int64'),
                                           dtype('int64'), dtype('int64'), dtype('float64'), dtype('float64'),
                                           dtype('float64'), dtype('float64'), dtype('float64'),
                                           dtype('float64'), dtype('float64'), dtype('float64'),
                                           dtype('float64'), dtype('float64'), dtype('float64'),
                                           dtype('float64'), dtype('float64'), dtype('float64'),
                                           dtype('float64'), dtype('bool'), dtype('int64'), dtype('int64'),
                                           dtype('int64'), dtype('int64'), dtype('int64'),
                                           dtype('int64'), dtype('int64'), dtype('float64'), dtype('float64')],
                               dtype=object)
        self.shapes = np.array([ 1,  1,  1,  1,  1,  1,  5,  5,  5, 11, 11, 11, 20, 20, 20, 20, 20,
                                            20, 20, 20, 20, 20, 20, 56, 20, 14, 20, 20, 20,
                                 5, 5])
        self.size_obs = 434

    def test_sum_shape_equal_size(self):
        obs = self.env.helper_observation(self.env)
        assert obs.size() == np.sum(obs.shape())

    def test_size(self):
        obs = self.env.helper_observation(self.env)
        obs.size()

    def test_proper_size(self):
        obs = self.env.helper_observation(self.env)
        assert obs.size() == self.size_obs

    def test_size_action_space(self):
        assert self.env.helper_observation.size() == self.size_obs

    def test_bus_conn_mat(self):
        obs = self.env.helper_observation(self.env)
        mat1 = obs.bus_connectivity_matrix()
        ref_mat = np.array([[1., 1., 0., 0., 1., 0., 0., 0., 0., 0., 0., 0., 0., 0.],
                           [1., 1., 1., 1., 1., 0., 0., 0., 0., 0., 0., 0., 0., 0.],
                           [0., 1., 1., 1., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.],
                           [0., 1., 1., 1., 1., 0., 1., 0., 1., 0., 0., 0., 0., 0.],
                           [1., 1., 0., 1., 1., 1., 0., 0., 0., 0., 0., 0., 0., 0.],
                           [0., 0., 0., 0., 1., 1., 0., 0., 0., 0., 1., 1., 1., 0.],
                           [0., 0., 0., 1., 0., 0., 1., 1., 1., 0., 0., 0., 0., 0.],
                           [0., 0., 0., 0., 0., 0., 1., 1., 0., 0., 0., 0., 0., 0.],
                           [0., 0., 0., 1., 0., 0., 1., 0., 1., 1., 0., 0., 0., 1.],
                           [0., 0., 0., 0., 0., 0., 0., 0., 1., 1., 1., 0., 0., 0.],
                           [0., 0., 0., 0., 0., 1., 0., 0., 0., 1., 1., 0., 0., 0.],
                           [0., 0., 0., 0., 0., 1., 0., 0., 0., 0., 0., 1., 1., 0.],
                           [0., 0., 0., 0., 0., 1., 0., 0., 0., 0., 0., 1., 1., 1.],
                           [0., 0., 0., 0., 0., 0., 0., 0., 1., 0., 0., 0., 1., 1.]])
        assert np.all(mat1 == ref_mat)

    def test_conn_mat(self):
        obs = self.env.helper_observation(self.env)
        mat = obs.connectivity_matrix()
        ref_mat = np.array([[0., 1., 1., 1., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
                            0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
                            0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
                            0., 0., 0., 0., 0., 0., 0., 0.],
                            [1., 0., 1., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
                             0., 0., 1., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
                             0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
                             0., 0., 0., 0., 0.],
                            [1., 1., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
                             0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
                             0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
                             0., 0., 0., 0., 0.],
                            [1., 0., 0., 0., 1., 1., 1., 1., 1., 0., 0., 0., 0., 0., 0., 0., 0.,
                             0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
                             0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
                             0., 0., 0., 0., 0.],
                            [0., 0., 0., 1., 0., 1., 1., 1., 1., 1., 0., 0., 0., 0., 0., 0., 0.,
                             0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
                             0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
                             0., 0., 0., 0., 0.],
                            [0., 0., 0., 1., 1., 0., 1., 1., 1., 0., 0., 0., 0., 1., 0., 0., 0.,
                             0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
                             0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
                             0., 0., 0., 0., 0.],
                            [0., 0., 0., 1., 1., 1., 0., 1., 1., 0., 0., 0., 0., 0., 0., 0., 0.,
                             0., 0., 0., 1., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
                             0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
                             0., 0., 0., 0., 0.],
                            [0., 0., 0., 1., 1., 1., 1., 0., 1., 0., 0., 0., 0., 0., 0., 0., 0.,
                             0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
                             0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
                             0., 0., 0., 0., 0.],
                            [0., 0., 0., 1., 1., 1., 1., 1., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
                             0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
                             0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
                             0., 0., 0., 0., 0.],
                            [0., 0., 0., 0., 1., 0., 0., 0., 0., 0., 1., 1., 1., 0., 0., 0., 0.,
                             0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
                             0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
                             0., 0., 0., 0., 0.]
                            ])
        assert np.all(mat[:10,:] == ref_mat)

    def test_observation_space(self):
        obs = self.env.helper_observation(self.env)
        assert self.env.observation_space.n == obs.size()

    def test_shape_correct(self):
        obs = self.env.helper_observation(self.env)
        assert obs.shape().shape == obs.dtype().shape
        assert np.all(obs.dtype() == self.dtypes)
        assert np.all(obs.shape() == self.shapes)

    def test_0_load_properly(self):
        # this test aims at checking that everything in setUp is working properly, eg that "ObsEnv" class has enough
        # information for example
        pass

    def test_1_generating_obs(self):
        # test that helper_obs is abl to generate a valid observation
        obs = self.env.helper_observation(self.env)
        pass

    def test_2_reset(self):
        # test that helper_obs is abl to generate a valid observation
        obs = self.env.helper_observation(self.env)
        assert obs.prod_p[0] is not None
        obs.reset()
        assert np.all(np.isnan(obs.prod_p))
        assert np.all(obs.dtype() == self.dtypes)
        assert np.all(obs.shape() == self.shapes)

    def test_3_reset(self):
        # test that helper_obs is able to generate a valid observation
        obs = self.env.helper_observation(self.env)
        obs2 = obs.copy()
        assert obs == obs2
        obs2.reset()
        assert np.all(np.isnan(obs2.prod_p))
        assert np.all(obs2.dtype() == self.dtypes)
        assert np.all(obs2.shape() == self.shapes)
        # assert obs.prod_p is not None

    def test_shapes_types(self):
        obs = self.env.helper_observation(self.env)
        dtypes = obs.dtype()
        assert np.all(dtypes == self.dtypes)
        shapes = obs.shape()
        assert np.all(shapes == self.shapes)

    def test_4_to_from_vect(self):
        # test that helper_obs is abl to generate a valid observation
        obs = self.env.helper_observation(self.env)
        obs2 = self.env.helper_observation(self.env)
        vect = obs.to_vect()
        assert vect.shape[0] == obs.size()
        obs2.reset()
        obs2.from_vect(vect)

        assert np.all(obs.dtype() == self.dtypes)
        assert np.all(obs.shape() == self.shapes)

        assert obs == obs2
        vect2 = obs2.to_vect()
        assert np.all(vect == vect2)

    def test_5_simulate_proper_timestep(self):
        obs_orig = self.env.helper_observation(self.env)
        action = self.env.helper_action_player({})
        action2 = self.env.helper_action_player({})

        simul_obs, simul_reward, simul_has_error, simul_info = obs_orig.simulate(action)
        real_obs, real_reward, real_has_error, real_info = self.env.step(action2)
        assert not real_has_error, "The powerflow diverged"

        # this is not true for every observation chronics, but we made sure in this files that the forecast were
        # without any noise, maintenance, nor hazards
        assert simul_obs == real_obs, "there is a mismatch in the observation, though they are supposed to be equal"
        assert np.abs(simul_reward - real_reward) <= self.tol_one

    def test_6_simulate_dont_affect_env(self):
        obs_orig = self.env.helper_observation(self.env)
        obs_orig = obs_orig.copy()

        for i in range(self.env.backend.n_line):
            # simulate lots of action
            tmp = np.full(self.env.backend.n_line, fill_value=False, dtype=np.bool)
            tmp[i] = True
            action = self.env.helper_action_player({"change_line_status": tmp})
            simul_obs, simul_reward, simul_has_error, simul_info = obs_orig.simulate(action)

        obs_after = self.env.helper_observation(self.env)
        assert obs_orig == obs_after

    def test_inspect_load(self):
        obs = self.env.helper_observation(self.env)
        dict_ = obs.state_of(load_id=0)
        assert "p" in dict_
        assert dict_["p"] == 18.8
        assert "q" in dict_
        assert dict_["q"] == 13.4
        assert "v" in dict_
        assert dict_["v"] == 141.075
        assert "bus" in dict_
        assert dict_["bus"] == 1
        assert "sub_id" in dict_
        assert dict_["sub_id"] == 1

    def test_inspect_gen(self):
        obs = self.env.helper_observation(self.env)
        dict_ = obs.state_of(gen_id=0)
        assert "p" in dict_
        assert dict_["p"] == 0.0
        assert "q" in dict_
        assert np.abs(dict_["q"] - 47.48313177017934) <= self.tol_one
        assert "v" in dict_
        assert np.abs(dict_["v"] - 141.075) <= self.tol_one
        assert "bus" in dict_
        assert dict_["bus"] == 1
        assert "sub_id" in dict_
        assert dict_["sub_id"] == 1

    def test_inspect_line(self):
        obs = self.env.helper_observation(self.env)
        dict_both = obs.state_of(line_id=0)
        assert "origin" in dict_both
        dict_ = dict_both["origin"]

        assert "p" in dict_
        assert np.abs(dict_["p"] - 109.77536682689008) <= self.tol_one
        assert "q" in dict_
        assert np.abs(dict_["q"] - -8.7165023030358) <= self.tol_one
        assert "v" in dict_
        assert np.abs(dict_["v"] - 143.1) <= self.tol_one
        assert "bus" in dict_
        assert dict_["bus"] == 1
        assert "sub_id" in dict_
        assert dict_["sub_id"] == 0

        assert "extremity" in dict_both
        dict_ = dict_both["extremity"]
        assert "p" in dict_
        assert np.abs(dict_["p"] - -107.69115512018216) <= self.tol_one
        assert "q" in dict_
        assert np.abs(dict_["q"] - 9.230658220781127) <= self.tol_one
        assert "v" in dict_
        assert np.abs(dict_["v"] - 141.075) <= self.tol_one
        assert "bus" in dict_
        assert dict_["bus"] == 1
        assert "sub_id" in dict_
        assert dict_["sub_id"] == 1

    def test_inspect_topo(self):
        obs = self.env.helper_observation(self.env)
        dict_ = obs.state_of(substation_id=1)
        assert "topo_vect" in dict_
        assert np.all(dict_["topo_vect"] == [1, 1, 1, 1, 1, 1])
        assert "nb_bus" in dict_
        assert dict_["nb_bus"] == 1

    def test_get_obj_connect_to(self):
        dict_ = self.env.helper_observation.get_obj_connect_to(substation_id=1)
        assert 'loads_id' in dict_
        assert np.all(dict_['loads_id'] == 0)
        assert 'generators_id' in dict_
        assert np.all(dict_['generators_id'] == 0)
        assert 'lines_or_id' in dict_
        assert np.all(dict_['lines_or_id'] == [7, 8, 9])
        assert 'lines_ex_id' in dict_
        assert np.all(dict_['lines_ex_id'] == 0)
        assert 'nb_elements' in dict_
        assert dict_['nb_elements'] == 6

    def test_to_dict(self):
        dict_ = self.env.helper_observation.to_dict()
        assert dict_ == self.dict_

    def test_from_dict(self):
        res = ObservationSpace.from_dict(self.dict_)
        assert res.n_gen == self.env.helper_observation.n_gen
        assert res.n_load == self.env.helper_observation.n_load
        assert res.n_line == self.env.helper_observation.n_line
        assert np.all(res.sub_info == self.env.helper_observation.sub_info)
        assert np.all(res.load_to_subid == self.env.helper_observation.load_to_subid)
        assert np.all(res.gen_to_subid == self.env.helper_observation.gen_to_subid)
        assert np.all(res.line_or_to_subid == self.env.helper_observation.line_or_to_subid)
        assert np.all(res.line_ex_to_subid == self.env.helper_observation.line_ex_to_subid)
        assert np.all(res.load_to_sub_pos == self.env.helper_observation.load_to_sub_pos)
        assert np.all(res.gen_to_sub_pos == self.env.helper_observation.gen_to_sub_pos)
        assert np.all(res.line_or_to_sub_pos == self.env.helper_observation.line_or_to_sub_pos)
        assert np.all(res.line_ex_to_sub_pos == self.env.helper_observation.line_ex_to_sub_pos)
        assert np.all(res.load_pos_topo_vect == self.env.helper_observation.load_pos_topo_vect)
        assert np.all(res.gen_pos_topo_vect == self.env.helper_observation.gen_pos_topo_vect)
        assert np.all(res.line_or_pos_topo_vect == self.env.helper_observation.line_or_pos_topo_vect)
        assert np.all(res.line_ex_pos_topo_vect == self.env.helper_observation.line_ex_pos_topo_vect)
        assert np.all(res.observationClass == self.env.helper_observation.observationClass)

    def test_json_serializable(self):
        dict_ = self.env.helper_observation.to_dict()
        res = json.dumps(obj=dict_, indent=4, sort_keys=True)

    def test_json_loadable(self):
        dict_ = self.env.helper_observation.to_dict()
        tmp = json.dumps(obj=dict_, indent=4, sort_keys=True)
        res = ObservationSpace.from_dict(json.loads(tmp))

        assert res.n_gen == self.env.helper_observation.n_gen
        assert res.n_load == self.env.helper_observation.n_load
        assert res.n_line == self.env.helper_observation.n_line
        assert np.all(res.sub_info == self.env.helper_observation.sub_info)
        assert np.all(res.load_to_subid == self.env.helper_observation.load_to_subid)
        assert np.all(res.gen_to_subid == self.env.helper_observation.gen_to_subid)
        assert np.all(res.line_or_to_subid == self.env.helper_observation.line_or_to_subid)
        assert np.all(res.line_ex_to_subid == self.env.helper_observation.line_ex_to_subid)
        assert np.all(res.load_to_sub_pos == self.env.helper_observation.load_to_sub_pos)
        assert np.all(res.gen_to_sub_pos == self.env.helper_observation.gen_to_sub_pos)
        assert np.all(res.line_or_to_sub_pos == self.env.helper_observation.line_or_to_sub_pos)
        assert np.all(res.line_ex_to_sub_pos == self.env.helper_observation.line_ex_to_sub_pos)
        assert np.all(res.load_pos_topo_vect == self.env.helper_observation.load_pos_topo_vect)
        assert np.all(res.gen_pos_topo_vect == self.env.helper_observation.gen_pos_topo_vect)
        assert np.all(res.line_or_pos_topo_vect == self.env.helper_observation.line_or_pos_topo_vect)
        assert np.all(res.line_ex_pos_topo_vect == self.env.helper_observation.line_ex_pos_topo_vect)
        assert np.all(res.observationClass == self.env.helper_observation.observationClass)


class TestObservationHazard(unittest.TestCase):
    def setUp(self):
        """
        The case file is a representation of the case14 as found in the ieee14 powergrid.
        :return:
        """
        # from ADNBackend import ADNBackend
        # self.backend = ADNBackend()
        # self.path_matpower = "/home/donnotben/Documents/RL4Grid/RL4Grid/data"
        # self.case_file = "ieee14_ADN.xml"
        # self.backend.load_grid(self.path_matpower, self.case_file)
        self.tolvect = 1e-2
        self.tol_one = 1e-5
        self.game_rules = RulesChecker()
        # pdb.set_trace()
        self.rewardClass = L2RPNReward
        self.reward_helper = self.rewardClass()
        self.obsClass = CompleteObservation
        self.parameters = Parameters()

        # powergrid
        self.backend = PandaPowerBackend()
        self.path_matpower = PATH_DATA_TEST_PP
        self.case_file = "test_case14.json"

        # chronics
        self.path_chron = os.path.join(PATH_CHRONICS, "chronics_with_hazards")
        self.chronics_handler = ChronicsHandler(chronicsClass=GridStateFromFile, path=self.path_chron)

        self.tolvect = 1e-2
        self.tol_one = 1e-5
        self.id_chron_to_back_load = np.array([0, 1, 10, 2, 3, 4, 5, 6, 7, 8, 9])

        # force the verbose backend
        self.backend.detailed_infos_for_cascading_failures = True

        self.names_chronics_to_backend = {"loads": {"2_C-10.61": 'load_1_0', "3_C151.15": 'load_2_1',
                                                    "14_C63.6": 'load_13_2', "4_C-9.47": 'load_3_3',
                                                    "5_C201.84": 'load_4_4',
                                                    "6_C-6.27": 'load_5_5', "9_C130.49": 'load_8_6',
                                                    "10_C228.66": 'load_9_7',
                                                    "11_C-138.89": 'load_10_8', "12_C-27.88": 'load_11_9',
                                                    "13_C-13.33": 'load_12_10'},
                                          "lines": {'1_2_1': '0_1_0', '1_5_2': '0_4_1', '9_10_16': '8_9_2',
                                                    '9_14_17': '8_13_3',
                                                    '10_11_18': '9_10_4', '12_13_19': '11_12_5', '13_14_20': '12_13_6',
                                                    '2_3_3': '1_2_7', '2_4_4': '1_3_8', '2_5_5': '1_4_9',
                                                    '3_4_6': '2_3_10',
                                                    '4_5_7': '3_4_11', '6_11_11': '5_10_12', '6_12_12': '5_11_13',
                                                    '6_13_13': '5_12_14', '4_7_8': '3_6_15', '4_9_9': '3_8_16',
                                                    '5_6_10': '4_5_17',
                                                    '7_8_14': '6_7_18', '7_9_15': '6_8_19'},
                                          "prods": {"1_G137.1": 'gen_0_4', "3_G36.31": "gen_2_1", "6_G63.29": "gen_5_2",
                                                    "2_G-56.47": "gen_1_0", "8_G40.43": "gen_7_3"},
                                          }

        # _parameters for the environment
        self.env_params = Parameters()

        self.env = Environment(init_grid_path=os.path.join(self.path_matpower, self.case_file),
                               backend=self.backend,
                               chronics_handler=self.chronics_handler,
                               parameters=self.env_params,
                               names_chronics_to_backend=self.names_chronics_to_backend,
                               rewardClass=self.rewardClass)

    def test_1_generating_obs_withhazard(self):
        # test that helper_obs is abl to generate a valid observation
        obs = self.env.get_obs()
        assert np.all(obs.time_before_line_reconnectable == [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        action = self.env.helper_action_player({})
        _ = self.env.step(action)
        obs = self.env.get_obs()
        assert np.all(obs.time_before_line_reconnectable == [0, 0, 0, 0, 12, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        _ = self.env.step(action)
        obs = self.env.get_obs()
        assert np.all(obs.time_before_line_reconnectable == [0, 0, 0, 0, 11, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])


class TestObservationMaintenance(unittest.TestCase):
    def setUp(self):
        """
        The case file is a representation of the case14 as found in the ieee14 powergrid.
        :return:
        """
        # from ADNBackend import ADNBackend
        # self.backend = ADNBackend()
        # self.path_matpower = "/home/donnotben/Documents/RL4Grid/RL4Grid/data"
        # self.case_file = "ieee14_ADN.xml"
        # self.backend.load_grid(self.path_matpower, self.case_file)
        self.tolvect = 1e-2
        self.tol_one = 1e-5
        self.game_rules = RulesChecker()
        # pdb.set_trace()
        self.rewardClass = L2RPNReward
        self.reward_helper = self.rewardClass()
        self.obsClass = CompleteObservation
        self.parameters = Parameters()

        # powergrid
        self.backend = PandaPowerBackend()
        self.path_matpower = PATH_DATA_TEST_PP
        self.case_file = "test_case14.json"

        # chronics
        self.path_chron = os.path.join(PATH_CHRONICS, "chronics_with_maintenance")
        self.chronics_handler = ChronicsHandler(chronicsClass=GridStateFromFile, path=self.path_chron)

        self.tolvect = 1e-2
        self.tol_one = 1e-5
        self.id_chron_to_back_load = np.array([0, 1, 10, 2, 3, 4, 5, 6, 7, 8, 9])

        # force the verbose backend
        self.backend.detailed_infos_for_cascading_failures = True

        self.names_chronics_to_backend = {"loads": {"2_C-10.61": 'load_1_0', "3_C151.15": 'load_2_1',
                                                    "14_C63.6": 'load_13_2', "4_C-9.47": 'load_3_3',
                                                    "5_C201.84": 'load_4_4',
                                                    "6_C-6.27": 'load_5_5', "9_C130.49": 'load_8_6',
                                                    "10_C228.66": 'load_9_7',
                                                    "11_C-138.89": 'load_10_8', "12_C-27.88": 'load_11_9',
                                                    "13_C-13.33": 'load_12_10'},
                                          "lines": {'1_2_1': '0_1_0', '1_5_2': '0_4_1', '9_10_16': '8_9_2',
                                                    '9_14_17': '8_13_3',
                                                    '10_11_18': '9_10_4', '12_13_19': '11_12_5', '13_14_20': '12_13_6',
                                                    '2_3_3': '1_2_7', '2_4_4': '1_3_8', '2_5_5': '1_4_9',
                                                    '3_4_6': '2_3_10',
                                                    '4_5_7': '3_4_11', '6_11_11': '5_10_12', '6_12_12': '5_11_13',
                                                    '6_13_13': '5_12_14', '4_7_8': '3_6_15', '4_9_9': '3_8_16',
                                                    '5_6_10': '4_5_17',
                                                    '7_8_14': '6_7_18', '7_9_15': '6_8_19'},
                                          "prods": {"1_G137.1": 'gen_0_4', "3_G36.31": "gen_2_1", "6_G63.29": "gen_5_2",
                                                    "2_G-56.47": "gen_1_0", "8_G40.43": "gen_7_3"},
                                          }

        # _parameters for the environment
        self.env_params = Parameters()

        self.env = Environment(init_grid_path=os.path.join(self.path_matpower, self.case_file),
                               backend=self.backend,
                               chronics_handler=self.chronics_handler,
                               parameters=self.env_params,
                               names_chronics_to_backend=self.names_chronics_to_backend,
                               rewardClass=self.rewardClass)

    def test_1_generating_obs_withmaintenance(self):
        # test that helper_obs is abl to generate a valid observation
        obs = self.env.get_obs()
        assert np.all(obs.time_next_maintenance == np.array([ -1,  -1,  -1,  -1,   1,  -1, 276,  -1,  -1,  -1,  -1,
                                                              -1,  -1, -1,  -1,  -1,  -1,  -1,  -1,  -1]))
        assert np.all(obs.duration_next_maintenance == np.array([ 0,  0,  0,  0, 12,  0, 12,  0,  0,  0,  0,  0,  0,
                                                                  0,  0,  0,  0, 0,  0,  0]))
        action = self.env.helper_action_player({})
        _ = self.env.step(action)
        obs = self.env.get_obs()
        assert np.all(obs.time_next_maintenance == np.array([ -1,  -1,  -1,  -1,   0,  -1, 275,  -1,  -1,  -1,  -1,
                                                              -1,  -1, -1,  -1,  -1,  -1,  -1,  -1,  -1]))
        assert np.all(obs.duration_next_maintenance == np.array([ 0,  0,  0,  0, 12,  0, 12,  0,  0,  0,  0,  0,  0,
                                                                  0,  0,  0,  0, 0,  0,  0]))
        _ = self.env.step(action)
        obs = self.env.get_obs()
        assert np.all(obs.time_next_maintenance == np.array([ -1,  -1,  -1,  -1,   0,  -1, 274,  -1,  -1,  -1,  -1,
                                                              -1,  -1, -1,  -1,  -1,  -1,  -1,  -1,  -1]))
        assert np.all(obs.duration_next_maintenance == np.array([ 0,  0,  0,  0, 11,  0, 12,  0,  0,  0,  0,  0,  0,
                                                                  0,  0,  0,  0, 0,  0,  0]))


class TestUpdateEnvironement(unittest.TestCase):
    def setUp(self):

        # Create env and obs in left hand
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore")
            self.lenv = make("case5_example")
            self.lobs = self.lenv.reset()

        # Create env and obs in right hand
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore")
            self.renv = make("case5_example")
            # Step once to make it different
            self.robs, _, _, _ = self.renv.step(self.renv.action_space())

        # Update left obs with right hand side environement
        self.lobs.update(self.renv)

    def tearDown(self):
        self.lenv.close()
        self.renv.close()

    def test_topology_updates(self):
        # Check left observation topology is updated to the right observation topology 
        assert np.all(self.lobs.timestep_overflow == self.robs.timestep_overflow)
        assert np.all(self.lobs.line_status == self.robs.line_status)
        assert np.all(self.lobs.topo_vect == self.robs.topo_vect)

    def test_prods_updates(self):
        # Check left loads are updated to the right loads 
        assert np.all(self.lobs.prod_p == self.robs.prod_p)
        assert np.all(self.lobs.prod_q == self.robs.prod_q)
        assert np.all(self.lobs.prod_v == self.robs.prod_v)

    def test_loads_updates(self):
        # Check left loads are updated to the right loads 
        assert np.all(self.lobs.load_p == self.robs.load_p)
        assert np.all(self.lobs.load_q == self.robs.load_q)
        assert np.all(self.lobs.load_v == self.robs.load_v)

    def test_lines_or_updates(self):
        # Check left loads are updated to the right loads 
        assert np.all(self.lobs.p_or == self.robs.p_or)
        assert np.all(self.lobs.q_or == self.robs.q_or)
        assert np.all(self.lobs.v_or == self.robs.v_or)
        assert np.all(self.lobs.a_or == self.robs.a_or)

    def test_lines_ex_updates(self):
        # Check left loads are updated to the rhs loads 
        assert np.all(self.lobs.p_ex == self.robs.p_ex)
        assert np.all(self.lobs.q_ex == self.robs.q_ex)
        assert np.all(self.lobs.v_ex == self.robs.v_ex)
        assert np.all(self.lobs.a_ex == self.robs.a_ex)

    def test_forecasts_updates(self):
        # Check left forecasts are updated to the rhs forecasts
        # Check forecasts sizes
        assert len(self.lobs._forecasted_inj) == len(self.robs._forecasted_inj)
        # Check each forecast
        for i in range(len(self.lobs._forecasted_inj)):
            # Check timestamp
            assert self.lobs._forecasted_inj[i][0] == self.robs._forecasted_inj[i][0]
            # Check load_p
            l_load_p = self.lobs._forecasted_inj[i][1]['injection']['load_p']
            r_load_p = self.robs._forecasted_inj[i][1]['injection']['load_p']
            assert np.all(l_load_p == r_load_p)
            # Check load_q
            l_load_q = self.lobs._forecasted_inj[i][1]['injection']['load_q']
            r_load_q = self.robs._forecasted_inj[i][1]['injection']['load_q']
            assert np.all(l_load_q == r_load_q)
            # Check prod_p
            l_prod_p = self.lobs._forecasted_inj[i][1]['injection']['prod_p']
            r_prod_p = self.robs._forecasted_inj[i][1]['injection']['prod_p']
            assert np.all(l_prod_p == r_prod_p)
            # Check prod_v
            l_prod_v = self.lobs._forecasted_inj[i][1]['injection']['prod_v']
            r_prod_v = self.robs._forecasted_inj[i][1]['injection']['prod_v']
            assert np.all(l_prod_v == r_prod_v)
            # Check maintenance
            l_maintenance = self.lobs._forecasted_inj[i][1]['maintenance']
            r_maintenance = self.robs._forecasted_inj[i][1]['maintenance']
            assert np.all(l_maintenance == r_maintenance)

        # Check relative flows
        assert np.all(self.lobs.rho == self.robs.rho)

    def test_cooldowns_updates(self):
        # Check left cooldowns are updated to the rhs CDs
        assert np.all(self.lobs.time_before_cooldown_line == self.robs.time_before_cooldown_line)
        assert np.all(self.lobs.time_before_cooldown_sub == self.robs.time_before_cooldown_sub)
        assert np.all(self.lobs.time_before_line_reconnectable == self.robs.time_before_line_reconnectable)
        assert np.all(self.lobs.time_next_maintenance == self.robs.time_next_maintenance)
        assert np.all(self.lobs.duration_next_maintenance == self.robs.duration_next_maintenance)

    def test_redispatch_updates(self):
        # Check left redispatch are updated to the rhs redispatches
        assert np.all(self.lobs.target_dispatch == self.robs.target_dispatch)
        assert np.all(self.lobs.actual_dispatch == self.robs.actual_dispatch)


class TestSimulateEqualsStep(unittest.TestCase):
    def setUp(self):
        # Create env
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore")
            self.env = make("case14_realistic")

        # Set forecasts to actual values so that simulate runs on the same numbers as step
        self.env.chronics_handler.real_data.data.prod_p_forecast = np.roll(self.env.chronics_handler.real_data.data.prod_p, -1, axis=0)
        self.env.chronics_handler.real_data.data.prod_v_forecast = np.roll(self.env.chronics_handler.real_data.data.prod_v, -1, axis=0)
        self.env.chronics_handler.real_data.data.load_p_forecast = np.roll(self.env.chronics_handler.real_data.data.load_p, -1, axis=0)
        self.env.chronics_handler.real_data.data.load_q_forecast = np.roll(self.env.chronics_handler.real_data.data.load_q, -1, axis=0)
        self.obs, _, _, _ = self.env.step(self.env.action_space({}))

        self.sim_obs = None
        self.step_obs = None
            
    def tearDown(self):
        self.env.close()

    def test_do_nothing(self):
        # Create action
        donothing_act = self.env.action_space()
        # Simulate & Step
        self.sim_obs, _, _, _ = self.obs.simulate(donothing_act)
        self.step_obs, _, _, _ = self.env.step(donothing_act)        
        # Test observations are the same
        assert self.sim_obs == self.step_obs

    def test_change_line_status(self):
        # Get change status vector
        change_status = self.env.action_space.get_change_line_status_vect()
        # Make a change
        change_status[0] = True
        # Create change action
        change_act = self.env.action_space({'change_line_status': change_status})
        # Simulate & Step
        self.sim_obs, _, _, _ = self.obs.simulate(change_act)
        self.step_obs, _, _, _ = self.env.step(change_act)        
        # Test observations are the same
        assert self.sim_obs == self.step_obs

    def test_set_line_status(self):
        # Get set status vector
        set_status = self.env.action_space.get_set_line_status_vect()
        # Make a change
        set_status[0] = -1 if self.obs.line_status[0] else 1
        # Create set action
        set_act = self.env.action_space({'set_line_status': set_status})
        # Simulate & Step
        self.sim_obs, _, _, _ = self.obs.simulate(set_act)
        self.step_obs, _, _, _ = self.env.step(set_act)        
        # Test observations are the same
        assert self.sim_obs == self.step_obs

    def test_change_bus(self):
        # Create a change bus action for all types
        change_act = self.env.action_space(
            {'change_bus':
             {
                 "loads_id": [0],
                 "generators_ids": [0],
                 "lines_or_id": [0],
                 "lines_ex_id": [0]
             }
            })
        # Simulate & Step
        self.sim_obs, _, _, _ = self.obs.simulate(change_act)
        self.step_obs, _, _, _ = self.env.step(change_act)
        # Test observations are the same
        assert self.sim_obs == self.step_obs

    def test_set_bus(self):
        # Increment buses from current topology
        new_load_bus = self.obs.topo_vect[self.obs.load_pos_topo_vect[0]] + 1
        new_gen_bus = self.obs.topo_vect[self.obs.gen_pos_topo_vect[0]] + 1
        new_lor_bus = self.obs.topo_vect[self.obs.line_or_pos_topo_vect[0]] + 1
        new_lex_bus = self.obs.topo_vect[self.obs.line_ex_pos_topo_vect[0]] + 1

        # Create a set bus action for all types
        set_act = self.env.action_space(
            {'set_bus':
             {
                 "loads_id": [(0, new_load_bus)],
                 "generators_ids": [(0, new_gen_bus)],
                 "lines_or_id": [(0, new_lor_bus)],
                 "lines_ex_id": [(0, new_lex_bus)]
             }
            })
        # Simulate & Step
        self.sim_obs, _, _, _ = self.obs.simulate(set_act)
        self.step_obs, _, _, _ = self.env.step(set_act)
        # Test observations are the same
        assert self.sim_obs == self.step_obs

    def test_redispatch(self):
        if DEACTIVATE_FAILING_TEST:
            return
        # Find first redispatchable generator
        gen_id = next((i for i, j in enumerate(self.obs.gen_redispatchable) if j), None) 
        # Create valid ramp up
        redisp_val = self.obs.gen_max_ramp_up[gen_id] / 2.0
        # Create redispatch action
        redisp_act = self.env.action_space({"redispatch": [(gen_id,redisp_val)]})
        # Simulate & Step
        self.sim_obs, _, _, _ = self.obs.simulate(redisp_act)
        self.step_obs, _, _, _ = self.env.step(redisp_act)
        # Test observations are the same
        assert self.sim_obs == self.step_obs

    def _multi_actions_sample(self):
        actions = []
        ## do_nothing action
        donothing_act = self.env.action_space()
        actions.append(donothing_act)

        ## change_status action
        # Get change status vector
        change_status = self.env.action_space.get_change_line_status_vect()
        # Make a change
        change_status[0] = True
        # Register change action
        change_act = self.env.action_space({'change_line_status': change_status})
        actions.append(change_act)

        ## set_status action
        # Get set status vector
        set_status = self.env.action_space.get_set_line_status_vect()
        # Make a change
        set_status[0] = -1 if self.obs.line_status[0] else 1
        # Register set action
        set_act = self.env.action_space({'set_line_status': set_status})
        actions.append(set_act)

        ## change_bus action
        # Register a change bus action for all types
        change_bus_act = self.env.action_space(
            {'change_bus':
             {
                 "loads_id": [0],
                 "generators_ids": [0],
                 "lines_or_id": [0],
                 "lines_ex_id": [0]
             }
            })
        actions.append(change_bus_act)

        ## set_bus_action
        # Increment buses from current topology
        new_load_bus = self.obs.topo_vect[self.obs.load_pos_topo_vect[0]] + 1
        new_gen_bus = self.obs.topo_vect[self.obs.gen_pos_topo_vect[0]] + 1
        new_lor_bus = self.obs.topo_vect[self.obs.line_or_pos_topo_vect[0]] + 1
        new_lex_bus = self.obs.topo_vect[self.obs.line_ex_pos_topo_vect[0]] + 1
        # Create a set bus action for all types
        set_bus_act = self.env.action_space(
            {'set_bus':
             {
                 "loads_id": [(0, new_load_bus)],
                 "generators_ids": [(0, new_gen_bus)],
                 "lines_or_id": [(0, new_lor_bus)],
                 "lines_ex_id": [(0, new_lex_bus)]
             }
            })
        actions.append(set_bus_act)

        ## redispatch action
        # Find first redispatchable generator
        gen_id = next((i for i, j in enumerate(self.obs.gen_redispatchable) if j), None) 
        # Create valid ramp up
        redisp_val = self.obs.gen_max_ramp_up[gen_id] / 2.0
        # Create redispatch action
        redisp_act = self.env.action_space({"redispatch": [(gen_id,redisp_val)]})
        actions.append(redisp_act)

        return actions
        
    def test_multi_simulate_last_do_nothing(self):
        if DEACTIVATE_FAILING_TEST:
            return
        actions = self._multi_actions_sample()

        # Add do_nothing last
        actions.append(self.env.action_space())

        # Simulate all actions
        for act in actions:
            self.sim_obs, _, _, _ = self.obs.simulate(act)
        # Step with last action
        self.step_obs, _, _, _ = self.env.step(actions[-1])
        # Test observations are the same
        assert self.sim_obs == self.step_obs

    def test_multi_simulate_last_change_line_status(self):
        if DEACTIVATE_FAILING_TEST:
            return
        actions = self._multi_actions_sample()

        ## Add change_line_status last
        # Get change status vector
        change_status = self.env.action_space.get_change_line_status_vect()
        # Make a change
        change_status[1] = True
        # Register change action
        change_act = self.env.action_space({'change_line_status': change_status})
        actions.append(change_act)

        # Simulate all actions
        for act in actions:
            self.sim_obs, _, _, _ = self.obs.simulate(act)
        # Step with last action
        self.step_obs, _, _, _ = self.env.step(actions[-1])
        # Test observations are the same
        assert self.sim_obs == self.step_obs
        
    def test_multi_simulate_last_set_line_status(self):
        if DEACTIVATE_FAILING_TEST:
            return
        actions = self._multi_actions_sample()
        ## Add set_status action last
        # Get set status vector
        set_status = self.env.action_space.get_set_line_status_vect()
        # Make a change
        set_status[1] = -1 if self.obs.line_status[1] else 1
        # Register set action
        set_act = self.env.action_space({'set_line_status': set_status})
        actions.append(set_act)
        
        # Simulate all actions
        for act in actions:
            self.sim_obs, _, _, _ = self.obs.simulate(act)
        # Step with last action
        self.step_obs, _, _, _ = self.env.step(actions[-1])
        # Test observations are the same
        assert self.sim_obs == self.step_obs

    def test_multi_simulate_last_change_bus(self):
        if DEACTIVATE_FAILING_TEST:
            return
        actions = self._multi_actions_sample()

        ## Add change_bus action last
        # Register a change bus action for all types
        change_bus_act = self.env.action_space(
            {'change_bus':
             {
                 "loads_id": [1],
                 "generators_ids": [1],
                 "lines_or_id": [1],
                 "lines_ex_id": [1]
             }
            })
        actions.append(change_bus_act)
        
        # Simulate all actions
        for act in actions:
            self.sim_obs, _, _, _ = self.obs.simulate(act)
        # Step with last action
        self.step_obs, _, _, _ = self.env.step(actions[-1])
        # Test observations are the same
        assert self.sim_obs == self.step_obs

    def test_multi_simulate_last_set_bus(self):
        if DEACTIVATE_FAILING_TEST:
            return
        actions = self._multi_actions_sample()
        ## Add set_bus_action last
        # Increment buses from current topology
        new_load_bus = self.obs.topo_vect[self.obs.load_pos_topo_vect[1]] + 1
        new_gen_bus = self.obs.topo_vect[self.obs.gen_pos_topo_vect[1]] + 1
        new_lor_bus = self.obs.topo_vect[self.obs.line_or_pos_topo_vect[1]] + 1
        new_lex_bus = self.obs.topo_vect[self.obs.line_ex_pos_topo_vect[1]] + 1
        # Create a set bus action for all types
        set_bus_act = self.env.action_space(
            {'set_bus':
             {
                 "loads_id": [(1, new_load_bus)],
                 "generators_ids": [(1, new_gen_bus)],
                 "lines_or_id": [(1, new_lor_bus)],
                 "lines_ex_id": [(1, new_lex_bus)]
             }
            })
        actions.append(set_bus_act)

        # Simulate all actions
        for act in actions:
            self.sim_obs, _, _, _ = self.obs.simulate(act)
        # Step with last action
        self.step_obs, _, _, _ = self.env.step(actions[-1])
        # Test observations are the same
        assert self.sim_obs == self.step_obs

    def test_multi_simulate_last_redispatch(self):
        if DEACTIVATE_FAILING_TEST:
            return
        actions = self._multi_actions_sample()

        ## Add redispatch action last
        # Find second redispatchable generator
        matches = 0
        gen_id = -1
        for i, j in enumerate(self.obs.gen_redispatchable):
            if j:
                matches += 1
                gen_id = i
            if matches == 2:
                break
        # Make sure we have a generator
        assert gen_id != -1
        # Create valid ramp up
        redisp_val = self.obs.gen_max_ramp_up[gen_id] / 2.0
        # Create redispatch action
        redisp_act = self.env.action_space({"redispatch": [(gen_id,redisp_val)]})
        actions.append(redisp_act)

        # Simulate all actions
        for act in actions:
            self.sim_obs, _, _, _ = self.obs.simulate(act)
        # Step with last action
        self.step_obs, _, _, _ = self.env.step(actions[-1])
        # Test observations are the same
        assert self.sim_obs == self.step_obs

## TODO test -- Add test to cover simulation vs step when there is a planned maintenance operation

        
if __name__ == "__main__":
    unittest.main()
