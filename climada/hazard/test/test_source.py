"""
Test read Hazard from file.
"""

import unittest
import numpy as np

from climada.hazard.source import DEF_VAR_MAT, DEF_VAR_EXCEL
from climada.hazard.base import Hazard
from climada.hazard.centroids.base import Centroids
from climada.util.constants import HAZ_TEST_MAT, HAZ_DEMO_XLS

class TestReaderMat(unittest.TestCase):
    '''Test reader functionality of the ExposuresExcel class'''

    def tearDown(self):
        """Set correct encapsulation variable name, as default."""
        DEF_VAR_MAT = {'field_name': 'hazard',
                        'var_name': {'per_id' : 'peril_ID',
                                     'even_id' : 'event_ID',
                                     'ev_name' : 'name',
                                     'freq' : 'frequency',
                                     'inten': 'intensity',
                                     'unit': 'units',
                                     'frac': 'fraction'
                                    },
                        'var_cent': {'cen_id' : 'centroid_ID',
                                     'lat' : 'lat',
                                     'lon' : 'lon'
                                    }
                      }

    def test_hazard_pass(self):
        ''' Read a hazard mat file correctly.'''
        # Read demo excel file
        hazard = Hazard()
        hazard.read(HAZ_TEST_MAT, 'TC')

        # Check results
        n_events = 14450
        n_centroids = 100

        self.assertEqual(hazard.units, 'm/s')

        self.assertEqual(hazard.centroids.coord.shape, (n_centroids, 2))

        self.assertEqual(hazard.event_id.dtype, int)
        self.assertEqual(hazard.event_id.shape, (n_events,))

        self.assertEqual(hazard.frequency.dtype, np.float)
        self.assertEqual(hazard.frequency.shape, (n_events,))

        self.assertEqual(hazard.intensity.dtype, np.float)
        self.assertEqual(hazard.intensity.shape, (n_events, n_centroids))
        self.assertEqual(hazard.intensity[12, 46], 12.071393519949979)
        self.assertEqual(hazard.intensity[13676, 49], 17.228323602220616)

        self.assertEqual(hazard.fraction.dtype, np.float)
        self.assertEqual(hazard.fraction.shape, (n_events, n_centroids))
        self.assertEqual(hazard.fraction[8454, 98], 1)
        self.assertEqual(hazard.fraction[85, 54], 0)

        self.assertEqual(len(hazard.event_name), n_events)
        self.assertEqual(hazard.event_name[124], 125)

        # tag hazard
        self.assertEqual(hazard.tag.file_name, HAZ_TEST_MAT)
        self.assertEqual(hazard.tag.description, \
                         ' TC hazard event set, generated 14-Nov-2017 10:09:05')
        self.assertEqual(hazard.tag.haz_type, 'TC')

        # tag centroids
        self.assertEqual(hazard.centroids.tag.file_name, HAZ_TEST_MAT)
        self.assertEqual(hazard.centroids.tag.description, '')

    def test_wrong_centroid_error(self):
        """ Read centroid separately from the hazard. Wrong centroid data in
        size """
        # Read demo excel file
        read_cen = Centroids(HAZ_TEST_MAT)
        read_cen.id = np.ones(12)
        # Read demo excel file
        hazard = Hazard()

        # Expected exception because centroid size is smaller than the
        # one provided in the intensity matrix
        with self.assertRaises(ValueError):
            hazard.read(HAZ_TEST_MAT, 'TC', centroids=read_cen)

#    def test_wrong_encapsulating_warning(self):
#        """ Warning is raised when FIELD_NAME is not encapsulating."""
#        DEF_VAR_MAT['field_name'] = 'wrong'
#        with self.assertLogs('climada.entity.impact_funcs.base', level='WARNING') as cm:
#            Hazard(HAZ_TEST_MAT, 'TC')
#        self.assertIn("Variables are not under: wrong.", cm.output[0])            

    def test_wrong_hazard_type_error(self):
        """ Error if provided hazard type different as contained"""
        hazard = Hazard()
        with self.assertRaises(ValueError):
            hazard.read(HAZ_TEST_MAT, 'WS')

    def test_centroid_hazard_pass(self):
        """ Read centroid separately from the hazard """
        # Read demo excel file
        description = 'One single file.'
        centroids = Centroids(HAZ_TEST_MAT, description)
        hazard = Hazard()
        hazard.read(HAZ_TEST_MAT, 'TC', description, centroids)

        n_centroids = 100
        self.assertEqual(centroids.coord.shape, (n_centroids, 2))
        self.assertEqual(centroids.coord[0][0], 21)
        self.assertEqual(centroids.coord[0][1], -84)
        self.assertEqual(centroids.coord[n_centroids-1][0], 30)
        self.assertEqual(centroids.coord[n_centroids-1][1], -75)
        self.assertEqual(centroids.id.dtype, int)
        self.assertEqual(centroids.id.shape, (n_centroids, ))
        self.assertEqual(centroids.id[0], 1)
        self.assertEqual(centroids.id[n_centroids-1], 100)

        # tag centroids
        self.assertEqual(hazard.centroids.tag.file_name, HAZ_TEST_MAT)
        self.assertEqual(hazard.centroids.tag.description, description)
        
    def test_wrong_file_fail(self):
        """ Read file intensity, fail."""
        new_var_names = DEF_VAR_MAT
        new_var_names['var_cent']['var_name']['cen_id'] = 'wrong name'
        hazard = Hazard()
        with self.assertRaises(KeyError):
            hazard.read(HAZ_TEST_MAT, 'TC', var_names=new_var_names)

class TestReaderExcel(unittest.TestCase):
    '''Test reader functionality of the Hazard class'''

    def tearDown(self):
        DEF_VAR_EXCEL = {'sheet_name': {'centroid' : 'centroids',
                                        'inten' : 'hazard_intensity',
                                        'freq' : 'hazard_frequency'
                                       },
                         'col_name': {'cen_id' : 'centroid_ID',
                                      'even_id' : 'event_ID',
                                      'freq' : 'frequency'
                                     },
                         'col_centroids': {'cen_id' : 'centroid_ID',
                                           'lat' : 'Latitude',
                                           'lon' : 'Longitude'
                                          }
                        }

    def test_hazard_pass(self):
        ''' Read an hazard excel file correctly.'''

        # Read demo excel file
        hazard = Hazard()
        description = 'One single file.'
        hazard.read(HAZ_DEMO_XLS, 'TC', description)

        # Check results
        n_events = 100
        n_centroids = 45

        self.assertEqual(hazard.units, 'NA')

        self.assertEqual(hazard.centroids.coord.shape, (n_centroids, 2))
        self.assertEqual(hazard.centroids.coord[0][0], -25.95)
        self.assertEqual(hazard.centroids.coord[0][1], 32.57)
        self.assertEqual(hazard.centroids.coord[n_centroids-1][0], -24.7)
        self.assertEqual(hazard.centroids.coord[n_centroids-1][1], 33.88)
        self.assertEqual(hazard.centroids.id.dtype, int)
        self.assertEqual(hazard.centroids.id[0], 4001)
        self.assertEqual(hazard.centroids.id[n_centroids-1], 4045)

        self.assertEqual(len(hazard.event_name), 100)
        self.assertEqual(hazard.event_name[12], 'event013')

        self.assertEqual(hazard.event_id.dtype, int)
        self.assertEqual(hazard.event_id.shape, (n_events,))
        self.assertEqual(hazard.event_id[0], 1)
        self.assertEqual(hazard.event_id[n_events-1], 100)

        self.assertEqual(hazard.frequency.dtype, np.float)
        self.assertEqual(hazard.frequency.shape, (n_events,))
        self.assertEqual(hazard.frequency[0], 0.01)
        self.assertEqual(hazard.frequency[n_events-2], 0.001)

        self.assertEqual(hazard.intensity.dtype, np.float)
        self.assertEqual(hazard.intensity.shape, (n_events, n_centroids))

        self.assertEqual(hazard.fraction.dtype, np.float)
        self.assertEqual(hazard.fraction.shape, (n_events, n_centroids))
        self.assertEqual(hazard.fraction[0, 0], 1)
        self.assertEqual(hazard.fraction[10, 19], 1)
        self.assertEqual(hazard.fraction[n_events-1, n_centroids-1], 1)

        # tag hazard
        self.assertEqual(hazard.tag.file_name, HAZ_DEMO_XLS)
        self.assertEqual(hazard.tag.description, description)
        self.assertEqual(hazard.tag.haz_type, 'TC')

        # tag centroids
        self.assertEqual(hazard.centroids.tag.file_name, HAZ_DEMO_XLS)
        self.assertEqual(hazard.centroids.tag.description, description)

    def test_wrong_centroid_fail(self):
        """ Read centroid separately from the hazard. Wrong centroid data in
        size """
        # Read demo excel file
        read_cen = Centroids(HAZ_DEMO_XLS)
        read_cen.id = np.ones(12)
        # Read demo excel file
        hazard = Hazard()

        # Expected exception because centroid size is smaller than the
        # one provided in the intensity matrix
        with self.assertRaises(ValueError):
            hazard.read(HAZ_DEMO_XLS, 'TC', centroids=read_cen)

    def test_centroid_hazard_pass(self):
        """ Read centroid separately from the hazard """

        # Read demo excel file
        description = 'One single file.'
        centroids = Centroids(HAZ_DEMO_XLS, description)
        hazard = Hazard()
        hazard.read(HAZ_DEMO_XLS, 'TC', description, centroids)

        n_centroids = 45
        self.assertEqual(hazard.centroids.coord.shape[0], n_centroids)
        self.assertEqual(hazard.centroids.coord.shape[1], 2)
        self.assertEqual(hazard.centroids.coord[0][0], -25.95)
        self.assertEqual(hazard.centroids.coord[0][1], 32.57)
        self.assertEqual(hazard.centroids.coord[n_centroids-1][0], -24.7)
        self.assertEqual(hazard.centroids.coord[n_centroids-1][1], 33.88)
        self.assertEqual(hazard.centroids.id.dtype, int)
        self.assertEqual(len(hazard.centroids.id), n_centroids)
        self.assertEqual(hazard.centroids.id[0], 4001)
        self.assertEqual(hazard.centroids.id[n_centroids-1], 4045)

        # tag centroids
        self.assertEqual(hazard.centroids.tag.file_name, HAZ_DEMO_XLS)
        self.assertEqual(hazard.centroids.tag.description, description)
        
    def test_wrong_file_fail(self):
        """ Read file intensity, fail."""
        new_var_names = DEF_VAR_EXCEL
        new_var_names['col_name']['cen_id'] = 'wrong name'
        hazard = Hazard()
        with self.assertRaises(KeyError):
            hazard.read(HAZ_DEMO_XLS, 'TC', var_names=new_var_names)

# Execute Tests
TESTS = unittest.TestLoader().loadTestsFromTestCase(TestReaderMat)
TESTS.addTests(unittest.TestLoader().loadTestsFromTestCase(TestReaderExcel))
unittest.TextTestRunner(verbosity=2).run(TESTS)
