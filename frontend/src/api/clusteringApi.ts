import { http, toApiResponse, ApiResponse } from "./http";

export interface Cluster {
  cluster: number;
  size: number;
  members: string[];
  centroid?: number[];
  features?: Record<string, number>;
}

export interface ClusterDistribution {
  clusters: Array<{ cluster: number; count: number }>;
}

export interface ClusterInsights {
  insights: Array<{
    cluster: number;
    description: string;
    characteristics: Record<string, any>;
  }>;
}

/**
 * Get clusters for campaigns or other entities
 */
export async function getClusters(
  entity: string = "campaign",
  k: number = 2
): Promise<ApiResponse<Cluster[]>> {
  return toApiResponse(http.get(`/api/model-inference/clusters`, { params: { entity, k } }));
}

/**
 * Get cluster distribution
 */
export async function getClusterDistribution(
  data: Array<Record<string, any>>,
  clusterCol: string = "cluster"
): Promise<ApiResponse<ClusterDistribution>> {
  return toApiResponse(
    http.post("/analytics-dashboard/cluster/distribution", {
      data,
      cluster_col: clusterCol,
    })
  );
}

/**
 * Get cluster insights and visualizations
 */
export async function getClusterInsights(
  data: Array<Record<string, any>>,
  clusterCol: string = "cluster",
  featureCols?: string[]
): Promise<ApiResponse<ClusterInsights>> {
  return toApiResponse(
    http.post("/analytics-dashboard/cluster/insights", {
      data,
      cluster_col: clusterCol,
      feature_cols: featureCols,
    })
  );
}
