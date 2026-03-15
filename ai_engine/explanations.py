def get_explanation(error):

    explanations = {
        "crash": "Application crashed due to runtime exception.",
        "permission": "Permission denied while accessing a resource.",
        "dependency": "Dependent service connection failure.",
        "memory": "Container terminated due to memory exhaustion.",
        "build": "Docker build process failed.",
        "timeout": "Application exceeded allowed execution time."
    }

    fixes = {
        "crash": "Restart container and inspect stack trace.",
        "permission": "Check file permissions and user privileges.",
        "dependency": "Ensure dependent service is running.",
        "memory": "Increase container memory limits.",
        "build": "Check Dockerfile and rebuild image.",
        "timeout": "Optimize application or increase timeout limit."
    }

    return explanations.get(error), fixes.get(error)