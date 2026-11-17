/**
 * Proxy di `ng serve`: in sviluppo il frontend chiama /api/ sullo stesso origin (come in produzione con nginx),
 * così il cookie di sessione è first-party e non serve CORS.
 * Avviare prima il backend: cd ../mamtab-backend/src && uvicorn main:app --reload --port 8000
 */
export default {
  '/api': { target: 'http://127.0.0.1:8000', secure: false, changeOrigin: false },
};
