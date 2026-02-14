import os
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
try:
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
except Exception:
    OTLPSpanExporter = None

def init_tracing(service_name: str = "RadioPlayerV3"):
    """Initialize OpenTelemetry tracing with a console exporter and optional OTLP exporter.

    Uses OTEL_EXPORTER_OTLP_ENDPOINT env var or defaults to http://localhost:4318
    (AI Toolkit Trace Collector) per best practices.
    """
    resource = Resource.create({"service.name": service_name})
    provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(provider)

    # Add OTLP exporter if available and endpoint is reachable
    otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4318")
    if OTLPSpanExporter is not None:
        try:
            otlp = OTLPSpanExporter(endpoint=otlp_endpoint)
            provider.add_span_processor(BatchSpanProcessor(otlp))
        except Exception:
            # ignore exporter errors; console exporter will still be attached
            pass

    # Always add a console exporter so traces are visible locally if OTLP is unavailable
    provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))

    # Return tracer for convenience
    return trace.get_tracer(service_name)
