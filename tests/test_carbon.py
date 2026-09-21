import unittest
import pandas as pd
from config import CARBON_FRACTION, CO2_TO_C_RATIO, ANNUAL_BASE_SEQ_RATE
from processing.carbon import calculate_carbon_metrics

class TestCarbonMetrics(unittest.TestCase):
    
    def setUp(self):
        # Create a sample DataFrame matching the structure needed
        self.df = pd.DataFrame({
            'coordinate_str': ['(24.5, 54.5)', '(24.6, 54.6)', '(24.7, 54.7)'],
            'GEDI_biomass_Mg_ha': [10.0, 50.0, 0.0],
            'GEDI_PAI': [1.0, 2.0, 0.5]
        })
        self.global_pai_mean = 1.0 # Easy reference for math
        
    def test_carbon_stock_calculation(self):
        result = calculate_carbon_metrics(self.df, self.global_pai_mean)
        
        # 10.0 * 0.47 = 4.7
        self.assertAlmostEqual(result.loc[0, 'carbon_stock_MgC_ha'], 4.7)
        # 50.0 * 0.47 = 23.5
        self.assertAlmostEqual(result.loc[1, 'carbon_stock_MgC_ha'], 23.5)
        
    def test_co2e_conversion(self):
        result = calculate_carbon_metrics(self.df, self.global_pai_mean)
        
        expected_co2e_0 = 4.7 * (44.0 / 12.0)
        self.assertAlmostEqual(result.loc[0, 'carbon_stock_tCO2e_ha'], expected_co2e_0)
        
    def test_monthly_absorption(self):
        result = calculate_carbon_metrics(self.df, self.global_pai_mean)
        
        # Node 1: PAI=1.0. Weight = 1.0/1.0 = 1.0. Rate = (6.0 * 1.0) / 12 = 0.5 MgC
        self.assertAlmostEqual(result.loc[0, 'monthly_absorption_MgC_ha'], 0.5)
        # CO2e = 0.5 * (44/12) = 1.8333...
        self.assertAlmostEqual(result.loc[0, 'monthly_absorption_tCO2e_ha'], 0.5 * (44.0/12.0))
        
        # Node 2: PAI=2.0. Weight = 2.0/1.0 = 2.0. Rate = (6.0 * 2.0) / 12 = 1.0 MgC
        self.assertAlmostEqual(result.loc[1, 'monthly_absorption_MgC_ha'], 1.0)
        
    def test_zero_biomass(self):
        result = calculate_carbon_metrics(self.df, self.global_pai_mean)
        
        self.assertEqual(result.loc[2, 'carbon_stock_MgC_ha'], 0.0)
        self.assertEqual(result.loc[2, 'carbon_stock_tCO2e_ha'], 0.0)
        
        # Zero biomass can still have PAI (e.g. young trees). 
        # So absorption > 0 is actually physically accurate in some mangrove growth models.
        # But if we specifically wanted 0, we'd add logic to carbon.py
        expected_abs = (ANNUAL_BASE_SEQ_RATE * (0.5/1.0)) / 12.0
        self.assertAlmostEqual(result.loc[2, 'monthly_absorption_MgC_ha'], expected_abs)

if __name__ == '__main__':
    unittest.main()
