<script lang="ts">
	import "../app.css";
	import type { PageProps } from "./$types";
	import { columns } from "./data";
	import DataTable from "./data-table.svelte";

	let { data }: PageProps = $props();

	import { getFilterValues } from "./data.remote";
	import ColumnFilter from "./ColumnFilter.svelte";
</script>

<svelte:head>
	<title>Lenovo Finder</title>
	<meta name="description" content="Advanced data table with filtering, sorting, pagination, and column management" />
</svelte:head>

<div class="px-5 py-3">
	<div class="p-5 grid grid-cols-2 gap-x-3">
		{#await getFilterValues()}
			<p>Loading...</p>
		{:then filterValues}
			{#each filterValues as filterValue}
				<ColumnFilter filterName={filterValue.column_name} options={filterValue.value} />
			{/each}
		{:catch error}
			<p>Error: {error.message}</p>
		{/await}
	</div>
	<div class="w-90% h-dvh">
		<DataTable {columns} data={data.products} />
	</div>
</div>
