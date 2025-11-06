import { useState, useCallback } from 'react';
import { nlpAPI } from '../services/api';

const useNLP = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [lastResult, setLastResult] = useState(null);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  const extractUML = useCallback(async (text) => {
    setIsLoading(true);
    setError(null);

    try {
      const result = await nlpAPI.extractUML(text);
      setLastResult(result);
      return result;
    } catch (err) {
      const errorMessage = err.message || 'Failed to process requirements';
      setError(errorMessage);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const validateText = useCallback(async (text) => {
    try {
      const validation = await nlpAPI.validateText(text);
      return validation;
    } catch (err) {
      const errorMessage = err.message || 'Validation failed';
      setError(errorMessage);
      throw err;
    }
  }, []);

  const preloadModels = useCallback(async () => {
    try {
      const result = await nlpAPI.preloadModels();
      return result;
    } catch (err) {
      const errorMessage = err.message || 'Failed to preload models';
      setError(errorMessage);
      throw err;
    }
  }, []);

  const healthCheck = useCallback(async () => {
    try {
      const health = await nlpAPI.healthCheck();
      return health;
    } catch (err) {
      const errorMessage = err.message || 'Health check failed';
      setError(errorMessage);
      throw err;
    }
  }, []);

  return {
    extractUML,
    validateText,
    preloadModels,
    healthCheck,
    isLoading,
    error,
    lastResult,
    clearError
  };
};

export default useNLP;