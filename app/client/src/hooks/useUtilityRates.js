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
      setUtilityData({
        rates: data.rates || [],
        mostLikelyRate: data.most_likely_rate,
        selectedRate: data.selected_rate,
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

  return { utilityData, fetchUtilityRates };
};
