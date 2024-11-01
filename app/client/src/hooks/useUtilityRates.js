import { useState } from 'react';
import { getCookie } from '../utils/formatters';

export const useUtilityRates = () => {
  const [utilityData, setUtilityData] = useState({
    rates: [],
    mostLikelyRate: null,
    selectedRate: null,
    yearlyCosts: [],
    loading: false,
    error: null
  });

  const fetchUtilityRates = async (formData) => {
    setUtilityData((prev) => ({ ...prev, loading: true, error: null }));
    try {
      const response = await fetch('/api/utility-rates/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify(formData),
        credentials: 'same-origin'
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to fetch utility rates');
      }

      const data = await response.json();

      // Preserve the currently selected rate if it exists in the new rates
      const currentSelected = utilityData.selectedRate;
      const newRates = data.rates || [];
      let newSelectedRate = data.most_likely_rate;

      if (currentSelected) {
        // Check if the current selection exists in the new rates
        const rateStillExists = newRates.find(rate => rate.label === currentSelected.label);
        if (rateStillExists) {
          newSelectedRate = rateStillExists;
        }
      }

      setUtilityData({
        rates: newRates,
        mostLikelyRate: data.most_likely_rate,
        selectedRate: newSelectedRate,
        yearlyCosts: data.yearly_costs || [],
        loading: false,
        error: null
      });
      return { success: true };
    } catch (error) {
      setUtilityData((prev) => ({
        ...prev,
        loading: false,
        error: error.message
      }));
      return { success: false, error: error.message };
    }
  };

  const updateSelectedRate = (rateLabel) => {
    setUtilityData((prev) => {
      const selectedRate = prev.rates.find(rate => rate.label === rateLabel);
      if (!selectedRate) return prev;
      return {
        ...prev,
        selectedRate: selectedRate
      };
    });
  };

  return { utilityData, fetchUtilityRates, updateSelectedRate };
};
