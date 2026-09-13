use axum::{
    extract::State,
    http::StatusCode,
    response::Html,
    routing::{get, post},
    Json, Router,
};
use serde::{Deserialize, Serialize};
use std::{env, net::SocketAddr, sync::Arc};
use tower_http::{cors::CorsLayer, services::ServeDir, trace::TraceLayer};

#[derive(Clone)]
struct AppState {
    agent_url: String,
    client: reqwest::Client,
}

#[derive(Debug, Deserialize, Serialize)]
struct QueryRequest {
    question: String,
    session_id: Option<String>,
    approved: Option<bool>,
}

#[derive(Debug, Serialize)]
struct HealthResponse {
    status: &'static str,
    service: &'static str,
    agent_url: String,
}

async fn health(State(state): State<Arc<AppState>>) -> Json<HealthResponse> {
    Json(HealthResponse {
        status: "ok",
        service: "nexus-edge",
        agent_url: state.agent_url.clone(),
    })
}

async fn query(
    State(state): State<Arc<AppState>>,
    Json(payload): Json<QueryRequest>,
) -> (StatusCode, Json<serde_json::Value>) {
    if payload.question.trim().is_empty() {
        return (
            StatusCode::BAD_REQUEST,
            Json(serde_json::json!({"error": "question must not be empty"})),
        );
    }

    match state
        .client
        .post(format!(
            "{}/v1/query",
            state.agent_url.trim_end_matches('/')
        ))
        .json(&payload)
        .send()
        .await
    {
        Ok(response) => {
            let status =
                StatusCode::from_u16(response.status().as_u16()).unwrap_or(StatusCode::BAD_GATEWAY);
            match response.json::<serde_json::Value>().await {
                Ok(body) => (status, Json(body)),
                Err(error) => (
                    StatusCode::BAD_GATEWAY,
                    Json(
                        serde_json::json!({"error": format!("agent returned invalid JSON: {error}")}),
                    ),
                ),
            }
        }
        Err(error) => (
            StatusCode::BAD_GATEWAY,
            Json(serde_json::json!({
                "error": "agent service unavailable",
                "detail": error.to_string()
            })),
        ),
    }
}

async fn index() -> Html<&'static str> {
    Html(include_str!("../static/index.html"))
}

#[tokio::main]
async fn main() {
    tracing_subscriber::fmt()
        .with_env_filter(env::var("RUST_LOG").unwrap_or_else(|_| "info".to_string()))
        .init();

    let host = env::var("RUST_API_HOST").unwrap_or_else(|_| "127.0.0.1".to_string());
    let port = env::var("RUST_API_PORT")
        .ok()
        .and_then(|value| value.parse::<u16>().ok())
        .unwrap_or(8080);
    let agent_url =
        env::var("AGENT_BASE_URL").unwrap_or_else(|_| "http://127.0.0.1:8000".to_string());
    let state = Arc::new(AppState {
        agent_url,
        client: reqwest::Client::new(),
    });

    let app = Router::new()
        .route("/", get(index))
        .route("/health", get(health))
        .route("/api/query", post(query))
        .nest_service("/static", ServeDir::new("static"))
        .layer(CorsLayer::permissive())
        .layer(TraceLayer::new_for_http())
        .with_state(state);

    let address: SocketAddr = format!("{host}:{port}")
        .parse()
        .expect("valid bind address");
    tracing::info!(%address, "nexus edge listening");
    let listener = tokio::net::TcpListener::bind(address)
        .await
        .expect("bind listener");
    axum::serve(listener, app).await.expect("serve HTTP");
}
