import React, { useState } from 'react';
import { Container, Card, CardContent, Typography, Alert } from '@mui/material';
import { UtilityForm } from './UtilityForm';
import { SelectedRatePlan } from './SelectedRatePlan';
import { CostProjection } from './CostProjection';
import { FeedbackSnackbar } from './FeedbackSnackbar';
import { useUtilityRates } from '../hooks/useUtilityRates';

const UtilityRateFinder = () => {
  const [formData, setFormData] = useState({
    address: '',
    consumption: 1000,
    escalator: 4,
    selectedRate: ''
  });

  const { utilityData, fetchUtilityRates, updateSelectedRate } = useUtilityRates();

  const [snackbar, setSnackbar] = useState({
    open: false,
    message: '',
    severity: 'info'
  });

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value
    }));
  };

  const handleRateSelect = (rateLabel) => {
    // Update both form data and utility data state
    setFormData((prev) => ({
      ...prev,
      selectedRate: rateLabel
    }));
    updateSelectedRate(rateLabel);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const result = await fetchUtilityRates(formData);

    if (result.success && utilityData.rates.length > 0) {
      // Always ensure the selected rate reflects the user's choice
      if (!formData.selectedRate) {
        const initialRate = utilityData.mostLikelyRate?.label || utilityData.rates[0].label;
        handleRateSelect(initialRate);
      }
    }

    setSnackbar({
      open: true,
      message: result.success
        ? 'Utility rates retrieved successfully!'
        : result.error,
      severity: result.success ? 'success' : 'error'
    });
  };



  const handleSnackbarClose = () => {
    setSnackbar((prev) => ({ ...prev, open: false }));
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Card>
        <CardContent>
          <Typography variant="h4" component="h1" gutterBottom>
            Utility Rate Calculator
          </Typography>
          <UtilityForm
            formData={formData}
            onInputChange={handleInputChange}
            onSubmit={handleSubmit}
            loading={utilityData.loading}
            rates={utilityData.rates}
            onRateSelect={handleRateSelect}
          />
          {utilityData.error && (
            <Alert severity="error" sx={{ mb: 3 }}>
              {utilityData.error}
            </Alert>
          )}
          <SelectedRatePlan
            selectedRate={utilityData.selectedRate}
            firstYearCost={utilityData.yearlyCosts[0]}
            isLoading={utilityData.loading}
          />
          <CostProjection
            yearlyCosts={utilityData.yearlyCosts}
            isLoading={utilityData.loading}
          />
        </CardContent>
      </Card>
      <FeedbackSnackbar
        open={snackbar.open}
        message={snackbar.message}
        severity={snackbar.severity}
        onClose={handleSnackbarClose}
      />
    </Container>
  );
};

export default UtilityRateFinder;
