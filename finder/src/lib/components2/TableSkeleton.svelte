<script lang="ts">
  const skeletonRows = Array.from({ length: 8 }, (_, i) => i);
  const skeletonCells = Array.from({ length: 10 }, (_, i) => i);
</script>

<div class="table-container">
  <!-- Header Skeleton -->
  <div class="table-header">
    <div class="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
      <div class="flex items-center gap-4">
        <div class="skeleton w-64 h-10 rounded-md"></div>
        <div class="flex items-center gap-2">
          <div class="skeleton w-12 h-6"></div>
          <div class="skeleton w-16 h-8 rounded"></div>
          <div class="skeleton w-12 h-6"></div>
        </div>
      </div>
      <div class="skeleton w-24 h-10 rounded-md"></div>
    </div>
  </div>

  <!-- Table Skeleton -->
  <div class="overflow-x-auto">
    <table class="w-full">
      <!-- Header Row -->
      <thead>
        <tr>
          {#each skeletonCells as cell}
            <th class="table-header-cell">
              <div class="skeleton w-20 h-4 rounded"></div>
            </th>
          {/each}
        </tr>
      </thead>
      
      <!-- Body Rows -->
      <tbody>
        {#each skeletonRows as row}
          <tr class="border-b border-gray-100">
            {#each skeletonCells as cell}
              <td class="table-cell">
                <div class="skeleton w-full h-4 rounded" style="width: {Math.random() * 60 + 40}%"></div>
              </td>
            {/each}
          </tr>
        {/each}
      </tbody>
    </table>
  </div>

  <!-- Pagination Skeleton -->
  <div class="px-6 py-4 bg-gray-50 border-t border-gray-200">
    <div class="flex items-center justify-between">
      <div class="skeleton w-48 h-5 rounded"></div>
      <div class="flex items-center gap-2">
        <div class="skeleton w-20 h-10 rounded-md"></div>
        <div class="skeleton w-24 h-5 rounded"></div>
        <div class="skeleton w-16 h-10 rounded-md"></div>
      </div>
    </div>
  </div>
</div>