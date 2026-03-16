"""
Kubernetes Deployment Manifests for AgentForge
===============================================

This module provides Kubernetes manifests and scaling utilities
for deploying AgentForge with auto-scaling Celery workers.

Components:
- Redis deployment (message broker)
- Celery worker deployment (auto-scaling)
- Backend API deployment
- HorizontalPodAutoscaler for workers
"""

import os
import yaml
from typing import Dict, Any, List

# Kubernetes namespace
NAMESPACE = os.environ.get('K8S_NAMESPACE', 'agentforge')

# Image configurations
IMAGES = {
    'backend': os.environ.get('BACKEND_IMAGE', 'agentforge/backend:latest'),
    'celery_worker': os.environ.get('CELERY_IMAGE', 'agentforge/celery-worker:latest'),
    'redis': os.environ.get('REDIS_IMAGE', 'redis:7-alpine'),
}


def generate_namespace() -> Dict[str, Any]:
    """Generate namespace manifest"""
    return {
        'apiVersion': 'v1',
        'kind': 'Namespace',
        'metadata': {
            'name': NAMESPACE,
            'labels': {
                'app': 'agentforge',
                'environment': os.environ.get('ENVIRONMENT', 'production')
            }
        }
    }


def generate_redis_deployment() -> Dict[str, Any]:
    """Generate Redis deployment for Celery broker"""
    return {
        'apiVersion': 'apps/v1',
        'kind': 'Deployment',
        'metadata': {
            'name': 'redis',
            'namespace': NAMESPACE,
            'labels': {'app': 'redis', 'component': 'broker'}
        },
        'spec': {
            'replicas': 1,
            'selector': {
                'matchLabels': {'app': 'redis'}
            },
            'template': {
                'metadata': {
                    'labels': {'app': 'redis', 'component': 'broker'}
                },
                'spec': {
                    'containers': [{
                        'name': 'redis',
                        'image': IMAGES['redis'],
                        'ports': [{'containerPort': 6379}],
                        'resources': {
                            'requests': {'memory': '128Mi', 'cpu': '100m'},
                            'limits': {'memory': '256Mi', 'cpu': '200m'}
                        },
                        'readinessProbe': {
                            'exec': {'command': ['redis-cli', 'ping']},
                            'initialDelaySeconds': 5,
                            'periodSeconds': 5
                        },
                        'livenessProbe': {
                            'exec': {'command': ['redis-cli', 'ping']},
                            'initialDelaySeconds': 10,
                            'periodSeconds': 10
                        }
                    }]
                }
            }
        }
    }


def generate_redis_service() -> Dict[str, Any]:
    """Generate Redis service"""
    return {
        'apiVersion': 'v1',
        'kind': 'Service',
        'metadata': {
            'name': 'redis',
            'namespace': NAMESPACE,
            'labels': {'app': 'redis'}
        },
        'spec': {
            'selector': {'app': 'redis'},
            'ports': [{
                'port': 6379,
                'targetPort': 6379,
                'protocol': 'TCP'
            }],
            'type': 'ClusterIP'
        }
    }


def generate_celery_worker_deployment(queue: str = 'default', replicas: int = 2) -> Dict[str, Any]:
    """Generate Celery worker deployment"""
    return {
        'apiVersion': 'apps/v1',
        'kind': 'Deployment',
        'metadata': {
            'name': f'celery-worker-{queue}',
            'namespace': NAMESPACE,
            'labels': {
                'app': 'celery-worker',
                'queue': queue,
                'component': 'worker'
            }
        },
        'spec': {
            'replicas': replicas,
            'selector': {
                'matchLabels': {'app': 'celery-worker', 'queue': queue}
            },
            'template': {
                'metadata': {
                    'labels': {
                        'app': 'celery-worker',
                        'queue': queue,
                        'component': 'worker'
                    }
                },
                'spec': {
                    'containers': [{
                        'name': 'worker',
                        'image': IMAGES['celery_worker'],
                        'command': [
                            'celery', '-A', 'services.celery_tasks', 'worker',
                            f'--queues={queue}',
                            '--loglevel=INFO',
                            '--concurrency=4'
                        ],
                        'env': [
                            {'name': 'CELERY_BROKER_URL', 'value': 'redis://redis:6379/0'},
                            {'name': 'CELERY_RESULT_BACKEND', 'value': 'redis://redis:6379/0'},
                            {
                                'name': 'MONGO_URL',
                                'valueFrom': {
                                    'secretKeyRef': {
                                        'name': 'agentforge-secrets',
                                        'key': 'mongo-url'
                                    }
                                }
                            },
                            {'name': 'DB_NAME', 'value': 'agentforge'}
                        ],
                        'resources': {
                            'requests': {'memory': '512Mi', 'cpu': '250m'},
                            'limits': {'memory': '1Gi', 'cpu': '500m'}
                        }
                    }]
                }
            }
        }
    }


def generate_worker_hpa(queue: str = 'default', min_replicas: int = 1, 
                        max_replicas: int = 10, target_cpu: int = 70) -> Dict[str, Any]:
    """Generate HorizontalPodAutoscaler for Celery workers"""
    return {
        'apiVersion': 'autoscaling/v2',
        'kind': 'HorizontalPodAutoscaler',
        'metadata': {
            'name': f'celery-worker-{queue}-hpa',
            'namespace': NAMESPACE
        },
        'spec': {
            'scaleTargetRef': {
                'apiVersion': 'apps/v1',
                'kind': 'Deployment',
                'name': f'celery-worker-{queue}'
            },
            'minReplicas': min_replicas,
            'maxReplicas': max_replicas,
            'metrics': [
                {
                    'type': 'Resource',
                    'resource': {
                        'name': 'cpu',
                        'target': {
                            'type': 'Utilization',
                            'averageUtilization': target_cpu
                        }
                    }
                },
                {
                    'type': 'Resource',
                    'resource': {
                        'name': 'memory',
                        'target': {
                            'type': 'Utilization',
                            'averageUtilization': 80
                        }
                    }
                }
            ],
            'behavior': {
                'scaleDown': {
                    'stabilizationWindowSeconds': 300,
                    'policies': [{
                        'type': 'Percent',
                        'value': 50,
                        'periodSeconds': 60
                    }]
                },
                'scaleUp': {
                    'stabilizationWindowSeconds': 0,
                    'policies': [
                        {'type': 'Percent', 'value': 100, 'periodSeconds': 15},
                        {'type': 'Pods', 'value': 4, 'periodSeconds': 15}
                    ],
                    'selectPolicy': 'Max'
                }
            }
        }
    }


def generate_backend_deployment(replicas: int = 2) -> Dict[str, Any]:
    """Generate backend API deployment"""
    return {
        'apiVersion': 'apps/v1',
        'kind': 'Deployment',
        'metadata': {
            'name': 'backend',
            'namespace': NAMESPACE,
            'labels': {'app': 'backend', 'component': 'api'}
        },
        'spec': {
            'replicas': replicas,
            'selector': {
                'matchLabels': {'app': 'backend'}
            },
            'template': {
                'metadata': {
                    'labels': {'app': 'backend', 'component': 'api'}
                },
                'spec': {
                    'containers': [{
                        'name': 'backend',
                        'image': IMAGES['backend'],
                        'ports': [{'containerPort': 8001}],
                        'env': [
                            {'name': 'CELERY_BROKER_URL', 'value': 'redis://redis:6379/0'},
                            {
                                'name': 'MONGO_URL',
                                'valueFrom': {
                                    'secretKeyRef': {
                                        'name': 'agentforge-secrets',
                                        'key': 'mongo-url'
                                    }
                                }
                            },
                            {
                                'name': 'FAL_KEY',
                                'valueFrom': {
                                    'secretKeyRef': {
                                        'name': 'agentforge-secrets',
                                        'key': 'fal-key'
                                    }
                                }
                            }
                        ],
                        'resources': {
                            'requests': {'memory': '512Mi', 'cpu': '250m'},
                            'limits': {'memory': '1Gi', 'cpu': '1000m'}
                        },
                        'readinessProbe': {
                            'httpGet': {'path': '/api/health', 'port': 8001},
                            'initialDelaySeconds': 10,
                            'periodSeconds': 5
                        },
                        'livenessProbe': {
                            'httpGet': {'path': '/api/health', 'port': 8001},
                            'initialDelaySeconds': 15,
                            'periodSeconds': 10
                        }
                    }]
                }
            }
        }
    }


def generate_backend_service() -> Dict[str, Any]:
    """Generate backend service"""
    return {
        'apiVersion': 'v1',
        'kind': 'Service',
        'metadata': {
            'name': 'backend',
            'namespace': NAMESPACE,
            'labels': {'app': 'backend'}
        },
        'spec': {
            'selector': {'app': 'backend'},
            'ports': [{
                'port': 8001,
                'targetPort': 8001,
                'protocol': 'TCP'
            }],
            'type': 'ClusterIP'
        }
    }


def generate_keda_scaledobject(queue: str = 'builds', 
                               min_replicas: int = 1,
                               max_replicas: int = 20) -> Dict[str, Any]:
    """Generate KEDA ScaledObject for queue-based scaling"""
    return {
        'apiVersion': 'keda.sh/v1alpha1',
        'kind': 'ScaledObject',
        'metadata': {
            'name': f'celery-worker-{queue}-keda',
            'namespace': NAMESPACE
        },
        'spec': {
            'scaleTargetRef': {
                'name': f'celery-worker-{queue}'
            },
            'minReplicaCount': min_replicas,
            'maxReplicaCount': max_replicas,
            'pollingInterval': 15,
            'cooldownPeriod': 300,
            'triggers': [{
                'type': 'redis',
                'metadata': {
                    'address': 'redis:6379',
                    'listName': queue,
                    'listLength': '5'  # Scale up when queue > 5
                }
            }]
        }
    }


def generate_all_manifests() -> List[Dict[str, Any]]:
    """Generate all Kubernetes manifests"""
    manifests = [
        generate_namespace(),
        generate_redis_deployment(),
        generate_redis_service(),
        generate_backend_deployment(),
        generate_backend_service(),
    ]
    
    # Add worker deployments and HPAs for each queue
    for queue in ['default', 'builds', 'assets', 'tests']:
        replicas = 3 if queue == 'builds' else 2
        max_replicas = 20 if queue == 'builds' else 10
        
        manifests.append(generate_celery_worker_deployment(queue, replicas))
        manifests.append(generate_worker_hpa(queue, 1, max_replicas))
    
    return manifests


def export_manifests(output_dir: str = '/app/kubernetes'):
    """Export all manifests to YAML files"""
    import os
    os.makedirs(output_dir, exist_ok=True)
    
    manifests = generate_all_manifests()
    
    # Write individual files
    files = {
        'namespace.yaml': [generate_namespace()],
        'redis.yaml': [generate_redis_deployment(), generate_redis_service()],
        'backend.yaml': [generate_backend_deployment(), generate_backend_service()],
        'workers.yaml': [],
        'autoscaling.yaml': []
    }
    
    for queue in ['default', 'builds', 'assets', 'tests']:
        files['workers.yaml'].append(generate_celery_worker_deployment(queue))
        files['autoscaling.yaml'].append(generate_worker_hpa(queue))
    
    for filename, docs in files.items():
        filepath = os.path.join(output_dir, filename)
        with open(filepath, 'w') as f:
            yaml.dump_all(docs, f, default_flow_style=False)
    
    # Write combined manifest
    with open(os.path.join(output_dir, 'all-in-one.yaml'), 'w') as f:
        yaml.dump_all(manifests, f, default_flow_style=False)
    
    return list(files.keys()) + ['all-in-one.yaml']


class K8sScaler:
    """Kubernetes scaling controller for AgentForge"""
    
    def __init__(self):
        self._k8s_available = False
        try:
            from kubernetes import client, config
            try:
                config.load_incluster_config()
            except:
                config.load_kube_config()
            self._apps_v1 = client.AppsV1Api()
            self._autoscaling_v2 = client.AutoscalingV2Api()
            self._k8s_available = True
        except Exception as e:
            print(f"Kubernetes not available: {e}")
    
    @property
    def is_available(self) -> bool:
        return self._k8s_available
    
    def scale_workers(self, queue: str, replicas: int) -> bool:
        """Manually scale workers for a queue"""
        if not self._k8s_available:
            return False
        
        try:
            body = {'spec': {'replicas': replicas}}
            self._apps_v1.patch_namespaced_deployment_scale(
                name=f'celery-worker-{queue}',
                namespace=NAMESPACE,
                body=body
            )
            return True
        except Exception as e:
            print(f"Failed to scale workers: {e}")
            return False
    
    def get_worker_status(self) -> Dict[str, Any]:
        """Get status of all worker deployments"""
        if not self._k8s_available:
            return {'available': False}
        
        try:
            deployments = self._apps_v1.list_namespaced_deployment(
                namespace=NAMESPACE,
                label_selector='component=worker'
            )
            
            status = {'available': True, 'workers': []}
            for dep in deployments.items:
                status['workers'].append({
                    'name': dep.metadata.name,
                    'desired': dep.spec.replicas,
                    'ready': dep.status.ready_replicas or 0,
                    'available': dep.status.available_replicas or 0
                })
            
            return status
        except Exception as e:
            return {'available': False, 'error': str(e)}
    
    def get_hpa_status(self) -> List[Dict[str, Any]]:
        """Get status of all HPAs"""
        if not self._k8s_available:
            return []
        
        try:
            hpas = self._autoscaling_v2.list_namespaced_horizontal_pod_autoscaler(
                namespace=NAMESPACE
            )
            
            return [{
                'name': hpa.metadata.name,
                'min_replicas': hpa.spec.min_replicas,
                'max_replicas': hpa.spec.max_replicas,
                'current_replicas': hpa.status.current_replicas,
                'desired_replicas': hpa.status.desired_replicas,
                'current_metrics': [
                    {
                        'name': m.resource.name if hasattr(m, 'resource') else 'unknown',
                        'current': m.resource.current.average_utilization if hasattr(m, 'resource') else None
                    }
                    for m in (hpa.status.current_metrics or [])
                ]
            } for hpa in hpas.items]
        except Exception as e:
            return []


# Global scaler instance
k8s_scaler = K8sScaler()
