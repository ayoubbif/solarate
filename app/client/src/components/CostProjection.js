import React, { useState } from 'react';
import { Box, Typography, Tabs, Tab } from '@mui/material';
import { CostProjectionChart } from './CostProjectionChart';
import { CostProjectionTable } from './CostProjectionTable';

export const CostProjection = ({ yearlyCosts }) => {
  const [viewMode, setViewMode] = useState('graph');

  if (yearlyCosts.length === 0) return null;

  // Helper function to check if a year is a leap year
  const isLeapYear = (year) => {
    const currentYear = new Date().getFullYear();
    const targetYear = currentYear + year;
    return (targetYear % 4 === 0 && targetYear % 100 !== 0) || targetYear % 400 === 0;
  };

  const chartData = yearlyCosts.map((cost, index) => {
    // Adjust the cost based on whether it's a leap year
    const adjustedCost = isLeapYear(index)
      ? cost * (366 / 365) // Increase cost proportionally for leap years
      : cost;

    // Calculate cumulative cost considering leap year adjustments
    const cumulativeCost = yearlyCosts
      .slice(0, index + 1)
      .reduce((sum, yearCost, yearIndex) => {
        const yearlyAdjustedCost = isLeapYear(yearIndex)
          ? yearCost * (366 / 365)
          : yearCost;
        return sum + yearlyAdjustedCost;
      }, 0);

    return {
      year: `Year ${index + 1}`,
      annualCost: adjustedCost,
      cumulativeCost: cumulativeCost,
      isLeapYear: isLeapYear(index)
    };
  });

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
