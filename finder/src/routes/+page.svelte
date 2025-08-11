<script lang="ts">
	import '../app.css';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();
</script>

{#each data.post.cols as col}
	<div>{col} </div>
{/each}


<!-- <script lang="ts">
  import DataTable from '$lib/components/DataTable.svelte';
  import { demoEmployees } from '$lib/data/demoData.js';
</script>

<svelte:head>
  <title>DataTable Pro - Advanced Employee Management</title>
  <meta name="description" content="Advanced data table with filtering, sorting, pagination, and column management" />
</svelte:head>

<DataTable data={demoEmployees} /> -->
