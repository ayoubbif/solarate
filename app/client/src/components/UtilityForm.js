import React from 'react';
import {
  Box,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  CircularProgress,
  Alert
} from '@mui/material';

export const UtilityForm = ({
  formData,
  onInputChange,
  onSubmit,
  loading,
  rates,
  onRateSelect,
  error
}) => {

  const handleRateChange = (event) => {
    const newRate = event.target.value;
    onInputChange({
      target: { name: 'selectedRate', value: newRate }
    });
    onRateSelect(newRate);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(e, formData.selectedRate);
  };

  return (
    <Box sx={{ maxWidth: 600, mx: 'auto', p: 3 }}>
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      <form onSubmit={handleSubmit}>
        <Box sx={{ display: 'grid', gap: 3, mb: 4 }}>
          <TextField
            fullWidth
            label="US Address"
            name="address"
            value={formData.address || ''}
            onChange={onInputChange}
            required
            placeholder="Enter your complete address"
            variant="outlined"
            error={!!formData.errors?.address}
            helperText={formData.errors?.address}
          />

          <TextField
            fullWidth
            label="Annual Consumption (kWh)"
            name="consumption"
            type="number"
            value={formData.consumption || ''}
            onChange={onInputChange}
            required
            inputProps={{ min: 1000, max: 10000 }}
            helperText="Enter a value between 1,000 and 10,000 kWh"
            variant="outlined"
            error={!!formData.errors?.consumption}
          />

          <TextField
            fullWidth
            label="Escalator Rate (%)"
            name="escalator"
            type="number"
            value={formData.escalator || ''}
            onChange={onInputChange}
            required
            inputProps={{ min: 4, max: 10, step: 0.1 }}
            helperText="Enter a value between 4% and 10%"
            variant="outlined"
            error={!!formData.errors?.escalator}
          />

          {rates.length > 0 && (
            <FormControl fullWidth>
              <InputLabel id="rate-select-label">Select Rate Plan</InputLabel>
              <Select
                labelId="rate-select-label"
                name="selectedRate"
                value={formData.selectedRate || ''}
                onChange={handleRateChange}
                label="Select Rate Plan"
              >
                {rates.map((rate) => (
                  <MenuItem key={rate.label} value={rate.label}>
                    {rate.utility} - {rate.name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          )}

          <Button
            type="submit"
            variant="contained"
            size="large"
            disabled={loading}
            sx={{
              height: 56,
              backgroundColor: 'primary.main',
              '&:hover': {
                backgroundColor: 'primary.dark',
              }
            }}
          >
            {loading ? (
              <CircularProgress size={24} sx={{ color: 'white' }} />
            ) : (
              'Calculate Rates'
            )}
          </Button>
        </Box>
      </form>
    </Box>
  );
};
