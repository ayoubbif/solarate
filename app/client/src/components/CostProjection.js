import React, { useState } from 'react';
import { Box, Typography, Tabs, Tab } from '@mui/material';
import {CostProjectionChart} from './CostProjectionChart';
import {CostProjectionTable} from './CostProjectionTable';

const isLeapYear = (year) => {
  const currentYear = new Date().getFullYear();
  const targetYear = currentYear + year;
  return (targetYear % 4 === 0 && targetYear % 100 !== 0) || targetYear % 400 === 0;
};

const getDaysInYear = (yearIndex) => {
  return isLeapYear(yearIndex) ? 366 : 365;
};

export const CostProjection = ({ dailyCost }) => {
    const [viewMode, setViewMode] = useState('graph');
  
    const calculateYearlyCosts = () => {
      return Array.from({ length: 20 }, (_, yearIndex) => {
        const daysInYear = getDaysInYear(yearIndex);
        const yearlyAmount = dailyCost * daysInYear;
        
        const previousYearsCost = Array.from({ length: yearIndex }, (_, prevIndex) => 
          dailyCost * getDaysInYear(prevIndex)
        ).reduce((sum, cost) => sum + cost, 0);
  
        return {
          year: `Year ${yearIndex + 1}`,
          daysInYear,
          annualCost: yearlyAmount,
          cumulativeCost: yearlyAmount + previousYearsCost
        };
      });
    };
  
    const chartData = calculateYearlyCosts();
    
    return (
      <Box sx={{ mt: 4 }}>
        <Typography variant="h6" sx={{ mb: 2 }}>
          20 Year Cost Projection
        </Typography>
        
        <Box sx={{ mb: 4 }}>
          <Tabs 
            value={viewMode} 
            onChange={(_, newValue) => setViewMode(newValue)}
            sx={{ mb: 2 }}
          >
            <Tab value="graph" label="Graph View" />
            <Tab value="table" label="Table View" />
          </Tabs>
        </Box>
  
        {viewMode === 'graph' ? (
          <CostProjectionChart chartData={chartData} />
        ) : (
          <CostProjectionTable chartData={chartData} />
        )}
      </Box>
    );
  };