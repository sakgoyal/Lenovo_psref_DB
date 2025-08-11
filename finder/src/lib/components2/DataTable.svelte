<script lang="ts">
  import { createTable, Render, Subscribe, createRender } from 'svelte-headless-table';
  import { addPagination, addSortBy, addTableFilter, addHiddenColumns, addSelectedRows } from 'svelte-headless-table/plugins';
  import { readable, writable, derived } from 'svelte/store';
  import { onMount } from 'svelte';
  import {
    ChevronUp,
    ChevronDown,
    Search,
    Filter,
    Settings,
    ChevronLeft,
    ChevronRight,
    Eye,
    EyeOff,
    ArrowUpDown
  } from 'lucide-svelte';
  import type { Employee } from '../types.js';
  import TableSkeleton from './TableSkeleton.svelte';
  import StatusBadge from './StatusBadge.svelte';

  export let data: Employee[] = [];

  let loading = true;
  let showColumnSettings = false;
  let globalFilterValue = '';

  // Simulate loading delay
  onMount(() => {
    setTimeout(() => {
      loading = false;
    }, 800);
  });

  const dataStore = derived(
    readable(data),
    ($data) => $data
  );

  const table = createTable(dataStore, {
    page: addPagination({
      initialPageSize: 25
    }),
    sort: addSortBy({
      initialSortKeys: [{ id: 'name', order: 'asc' }]
    }),
    filter: addTableFilter({
      fn: ({ filterValue, value }) => {
        if (!filterValue) return true;
        return value.toLowerCase().includes(filterValue.toLowerCase());
      }
    }),
    hide: addHiddenColumns({
      initialHiddenColumnIds: []
    }),
    select: addSelectedRows()
  });

  const columns = table.createColumns([
    table.column({
      accessor: 'id',
      header: 'ID',
      plugins: {
        sort: { disable: false },
        filter: { exclude: true }
      }
    }),
    table.column({
      accessor: 'name',
      header: 'Name',
      plugins: {
        sort: { disable: false }
      }
    }),
    table.column({
      accessor: 'email',
      header: 'Email',
      plugins: {
        sort: { disable: false }
      }
    }),
    table.column({
      accessor: 'position',
      header: 'Position',
      plugins: {
        sort: { disable: false }
      }
    }),
    table.column({
      accessor: 'department',
      header: 'Department',
      plugins: {
        sort: { disable: false }
      }
    }),
    table.column({
      accessor: 'salary',
      header: 'Salary',
      cell: ({ value }) => `$${value.toLocaleString()}`,
      plugins: {
        sort: { disable: false }
      }
    }),
    table.column({
      accessor: 'startDate',
      header: 'Start Date',
      cell: ({ value }) => value.toLocaleDateString(),
      plugins: {
        sort: { disable: false }
      }
    }),
    table.column({
      accessor: 'isActive',
      header: 'Status',
      cell: ({ value }) => createRender(StatusBadge, { active: value }),
      plugins: {
        sort: { disable: false },
        filter: { exclude: true }
      }
    }),
    table.column({
      accessor: 'projectsCompleted',
      header: 'Projects',
      plugins: {
        sort: { disable: false }
      }
    })
  ]);

  const { headerRows, pageRows, tableAttrs, tableBodyAttrs, pluginStates } =
    table.createViewModel(columns);

  const { hasNextPage, hasPreviousPage, pageIndex, pageSize, pageCount } = pluginStates.page;
  const { sortKeys } = pluginStates.sort;
  const { filterValue } = pluginStates.filter;
  const { hiddenColumnIds } = pluginStates.hide;

  $: $filterValue = globalFilterValue;

  const pageSizeOptions = [10, 25, 50, 100];

  function toggleColumnVisibility(columnId: string) {
    const current = $hiddenColumnIds;
    if (current.includes(columnId)) {
      hiddenColumnIds.set(current.filter(id => id !== columnId));
    } else {
      hiddenColumnIds.set([...current, columnId]);
    }
  }
</script>

<div class="p-6 max-w-full">
  <div class="mb-6">
    <h1 class="text-2xl font-bold text-gray-100 mb-2">Employee Data Management</h1>
    <p class="text-gray-300">Advanced data table with filtering, sorting, and pagination</p>
  </div>

  {#if loading}
    <TableSkeleton />
  {:else}
    <div class="table-container animate-fade-in">
      <!-- Table Controls -->
      <div class="table-header">
        <div class="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
          <div class="flex items-center gap-4">
            <!-- Global Search -->
            <div class="relative">
              <Search class="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <input
                type="text"
                placeholder="Search all columns..."
                bind:value={globalFilterValue}
                class="pl-10 pr-4 py-2 border border-gray-600 bg-gray-700 text-gray-100 placeholder-gray-400 rounded-md text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500 w-64"
              />
            </div>

            <!-- Page Size Selector -->
            <div class="flex items-center gap-2">
              <span class="text-sm text-gray-300">Show</span>
              <select bind:value={$pageSize} class="border border-gray-600 bg-gray-700 text-gray-100 rounded px-2 py-1 text-sm">
                {#each pageSizeOptions as size}
                  <option value={size}>{size}</option>
                {/each}
              </select>
              <span class="text-sm text-gray-300">rows</span>
            </div>
          </div>

          <!-- Column Settings -->
          <div class="relative">
            <button
              on:click={() => showColumnSettings = !showColumnSettings}
              class="btn-secondary"
            >
              <Settings class="w-4 h-4 mr-2" />
              Columns
            </button>

            {#if showColumnSettings}
              <div class="absolute right-0 top-12 bg-gray-800 border border-gray-600 rounded-lg shadow-lg p-4 z-10 min-w-48">
                <h3 class="font-medium text-gray-100 mb-3">Show/Hide Columns</h3>
                <div class="space-y-2">
                  {#each columns as column}
                    {@const columnId = column.id}
                    <label class="flex items-center gap-2 text-sm">
                      <input
                        type="checkbox"
                        checked={!$hiddenColumnIds.includes(columnId)}
                        on:change={() => toggleColumnVisibility(columnId)}
                        class="rounded border-gray-600 bg-gray-700 text-primary-600 focus:ring-primary-500"
                      />
                      <span class="capitalize">{columnId}</span>
                      {#if $hiddenColumnIds.includes(columnId)}
                        <EyeOff class="w-3 h-3 text-gray-400" />
                      {:else}
                        <Eye class="w-3 h-3 text-gray-500" />
                      {/if}
                    </label>
                  {/each}
                </div>
              </div>
            {/if}
          </div>
        </div>
      </div>

      <!-- Table -->
      <div class="overflow-x-auto table-scroll">
        <table {...$tableAttrs} class="w-full">
          <thead>
            {#each $headerRows as headerRow}
              <Subscribe rowAttrs={headerRow.attrs()}>
                <tr>
                  {#each headerRow.cells as cell (cell.id)}
                    <Subscribe attrs={cell.attrs()} let:attrs props={cell.props()} let:props>
                      <th {...attrs} class="table-header-cell text-left">
                        <div class="flex items-center gap-2">
                          <Render of={cell.render()} />
                          {#if props.sort.order === 'asc'}
                            <ChevronUp class="w-4 h-4 text-primary-600" />
                          {:else if props.sort.order === 'desc'}
                            <ChevronDown class="w-4 h-4 text-primary-600" />
                          {:else if props.sort.order === undefined}
                            <ArrowUpDown class="w-4 h-4 text-gray-400" />
                          {/if}
                        </div>
                      </th>
                    </Subscribe>
                  {/each}
                </tr>
              </Subscribe>
            {/each}
          </thead>
          <tbody {...$tableBodyAttrs}>
            {#each $pageRows as row (row.id)}
              <Subscribe rowAttrs={row.attrs()}>
                <tr class="hover:bg-gray-700 transition-colors">
                  {#each row.cells as cell (cell.id)}
                    <Subscribe attrs={cell.attrs()}>
                      <td class="table-cell">
                        <Render of={cell.render()} />
                      </td>
                    </Subscribe>
                  {/each}
                </tr>
              </Subscribe>
            {/each}
          </tbody>
        </table>
      </div>

      <!-- Pagination -->
      <div class="px-6 py-4 bg-gray-700 border-t border-gray-600">
        <div class="flex flex-col sm:flex-row items-center justify-between gap-4">
          <div class="text-sm text-gray-300">
            Showing {($pageIndex * $pageSize) + 1} to {Math.min(($pageIndex + 1) * $pageSize, data.length)} of {data.length} results
          </div>

          <div class="flex items-center gap-2">
            <button
              on:click={() => $pageIndex = $pageIndex - 1}
              disabled={!$hasPreviousPage}
              class="btn-secondary disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <ChevronLeft class="w-4 h-4" />
              Previous
            </button>

            <span class="px-4 py-2 text-sm text-gray-300">
              Page {$pageIndex + 1} of {$pageCount}
            </span>

            <button
              on:click={() => $pageIndex = $pageIndex + 1}
              disabled={!$hasNextPage}
              class="btn-secondary disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Next
              <ChevronRight class="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  {/if}
</div>

<!-- Click outside to close column settings -->
{#if showColumnSettings}
  <div
    class="fixed inset-0 z-0"
    on:click={() => showColumnSettings = false}
  ></div>
{/if}
