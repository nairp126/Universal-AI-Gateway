import os
import logging
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

logger = logging.getLogger(__name__)

def setup_tracing(app):
    """Initialize OpenTelemetry distributed tracing."""
    enable_tracing = os.getenv("ENABLE_TRACING", "true").lower() == "true"
    
    resource = Resource.create({
        "service.name": os.getenv("APP_NAME", "universal-llm-gateway"),
        "service.version": os.getenv("APP_VERSION", "1.0.0"),
        "deployment.environment": os.getenv("ENVIRONMENT", "development")
    })
    
    provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(provider)
    
    if enable_tracing:
        otlp_endpoint = os.getenv("OTLP_ENDPOINT", "http://jaeger:4317")
        try:
            exporter = OTLPSpanExporter(endpoint=otlp_endpoint, insecure=True)
            span_processor = BatchSpanProcessor(exporter)
            provider.add_span_processor(span_processor)
            logger.info(f"OpenTelemetry tracing enabled. OTLP endpoint: {otlp_endpoint}")
            
            # Instrument FastAPI
            FastAPIInstrumentor.instrument_app(app)
        except Exception as e:
            logger.error(f"Failed to initialize OpenTelemetry exporter: {e}")
    else:
        logger.info("OpenTelemetry OTLP exporting is disabled.")

def get_tracer(name: str):
    """Get a tracer instance for manual instrumentation."""
    return trace.get_tracer(name)
