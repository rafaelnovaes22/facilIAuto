# Implementation Plan - API Routing Fix

- [x] 1. Update backend API routes to support /api prefix





  - Add new routes with `/api` prefix for all endpoints
  - Keep existing routes without prefix for backward compatibility
  - Improve response when no dealerships found in region
  - Add detailed logging for debugging
  - _Requirements: 1.1, 1.2, 1.3, 2.1, 2.5, 5.1, 5.2, 5.3_

- [x] 2. Update frontend API service configuration





  - Remove `/api` prefix from all endpoint calls in `api.ts`
  - Configure baseURL to use environment variable `VITE_API_URL`
  - Add request interceptor for detailed logging
  - Improve response interceptor with specific error handling by type
  - Add session_id to all logs for traceability
  - _Requirements: 1.1, 1.2, 3.1, 3.2, 3.3, 4.1, 4.2, 4.3, 4.4, 5.1, 5.2, 5.3, 5.4_

- [x] 3. Simplify Vite proxy configuration





  - Remove rewrite rule from proxy configuration in `vite.config.ts`
  - Update proxy to forward `/api` prefix to backend
  - Document proxy behavior for development environment
  - _Requirements: 1.4, 3.1_

- [x] 4. Improve error handling in ResultsPage





  - Add specific error states for different error types (network, no_dealerships, server, validation)
  - Display user-friendly messages for each error type
  - Add "Retry" button for network and server errors
  - Add "Edit Location" button when no dealerships in state
  - Suggest nearby states with dealerships when applicable
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 4.1, 4.2, 4.3, 4.4, 4.5_

- [x] 5. Configure environment variables





  - Create `.env.development` file with `VITE_API_URL=http://localhost:8000`
  - Document Railway environment variable configuration in deployment docs
  - Add environment variable validation on app startup
  - _Requirements: 3.1, 3.2, 3.3, 3.5_

- [x] 6. Update QuestionnairePage error handling





  - Add error boundary for API failures during questionnaire
  - Display error messages when recommendation request fails
  - Add retry logic with exponential backoff
  - _Requirements: 4.1, 4.2, 4.3, 4.5_

- [ ]* 7. Add integration tests for API routing
  - Test `/recommend` endpoint works in development
  - Test `/api/recommend` endpoint works with new backend routes
  - Test response when no dealerships in selected state
  - Test CORS headers are correctly configured
  - _Requirements: 1.1, 1.2, 1.3, 2.1_

- [ ]* 8. Add unit tests for error handling
  - Test API service error interceptor handles all error types
  - Test ResultsPage displays correct messages for each error type
  - Test retry button functionality
  - Test logging includes session_id and required details
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 5.1, 5.2, 5.3, 5.4_

- [ ] 9. Update deployment documentation
  - Document environment variable setup for Railway
  - Add troubleshooting section for 405 errors
  - Document API routing behavior in dev vs production
  - Add monitoring recommendations for API errors
  - _Requirements: 3.2, 5.5_

- [ ] 10. Validate fix in production
  - Deploy changes to Railway
  - Test with state that has no dealerships
  - Verify no 405 errors in browser console
  - Check logs for proper error tracking
  - Monitor error rates after deployment
  - _Requirements: 1.2, 1.3, 2.1, 2.5, 5.5_
