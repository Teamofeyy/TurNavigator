import { PlannerApp } from "@/components/planner-app";
import { listCities } from "@/lib/travel-context-api";

export const dynamic = "force-dynamic";

async function loadInitialCities() {
  try {
    return {
      cities: await listCities(),
      loadError: null,
    };
  } catch (error) {
    return {
      cities: [],
      loadError:
        error instanceof Error
          ? error.message
          : "Не удалось загрузить список городов.",
    };
  }
}

export default async function Home() {
  const { cities, loadError } = await loadInitialCities();
  return <PlannerApp initialCities={cities} loadError={loadError} />;
}
