<template>
  <div class="container-fluid p-3">
    <!-- Breadcrumb -->
    <div class="small text-secondary mb-1">Home / admin / Reports</div>

    <!-- Page header -->
    <div class="d-flex justify-content-between align-items-center mb-3">
      <h3 class="mb-0">Reports &amp; Statistics</h3>
      <button
        class="btn btn-outline-secondary btn-sm"
        :disabled="loading"
        @click="loadReports"
      >
        Refresh
      </button>
    </div>

    <!-- Error banner -->
    <div v-if="error" class="alert alert-danger py-2">{{ error }}</div>

    <!-- Summary cards -->
    <div class="row g-3 mb-3">
      <div
        v-for="card in summaryCards"
        :key="card.label"
        class="col-6 col-lg-3"
      >
        <div class="card h-100">
          <div class="card-body">
            <div class="small text-secondary">{{ card.label }}</div>
            <div class="fs-4 fw-bold">{{ card.value }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Charts: examinations by type & bookings by status -->
    <div class="row g-3 mb-3">
      <div class="col-lg-6">
        <div class="card h-100">
          <div class="card-body">
            <h5 class="h6 fw-bold">Examinations by Type</h5>

            <div
              v-for="item in report.examinations_by_type || []"
              :key="item.label"
              class="mb-3"
            >
              <div class="d-flex justify-content-between small mb-1">
                <span>{{ item.label }}</span>
                <span>{{ item.count }}</span>
              </div>
              <div class="progress">
                <div
                  class="progress-bar"
                  :style="{ width: percentOfTotal(item.count, report.examinations_by_type) }"
                />
              </div>
            </div>

            <p
              v-if="!report.examinations_by_type?.length"
              class="text-secondary small mb-0"
            >
              No examination data.
            </p>
          </div>
        </div>
      </div>

      <div class="col-lg-6">
        <div class="card h-100">
          <div class="card-body">
            <h5 class="h6 fw-bold">Bookings by Status</h5>

            <div
              v-for="item in report.bookings_by_status || []"
              :key="item.label"
              class="mb-3"
            >
              <div class="d-flex justify-content-between small mb-1">
                <span>{{ item.label }}</span>
                <span>{{ item.count }}</span>
              </div>
              <div class="progress">
                <div
                  class="progress-bar bg-success"
                  :style="{ width: percentOfTotal(item.count, report.bookings_by_status) }"
                />
              </div>
            </div>

            <p
              v-if="!report.bookings_by_status?.length"
              class="text-secondary small mb-0"
            >
              No booking data.
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- Tables: examiner activity, monthly summary, student performance -->
    <div class="row g-3">
      <!-- Most Active Examiners -->
      <div class="col-lg-6">
        <div class="card h-100">
          <div class="card-body">
            <h5 class="h6 fw-bold">Most Active Examiners</h5>
            <div class="table-responsive">
              <table class="table table-sm">
                <thead>
                  <tr>
                    <th>Examiner</th>
                    <th>Slots</th>
                    <th>Bookings</th>
                    <th>Evaluations</th>
                  </tr>
                </thead>
                <tbody>
                  <tr
                    v-for="row in report.examiner_activity || []"
                    :key="row.examiner_name"
                  >
                    <td>{{ row.examiner_name }}</td>
                    <td>{{ row.slots }}</td>
                    <td>{{ row.bookings }}</td>
                    <td>{{ row.evaluations }}</td>
                  </tr>
                  <tr v-if="!report.examiner_activity?.length">
                    <td colspan="4" class="text-secondary">No examiner activity.</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>

      <!-- Monthly Examination Summary -->
      <div class="col-lg-6">
        <div class="card h-100">
          <div class="card-body">
            <h5 class="h6 fw-bold">Monthly Examination Summary</h5>
            <div class="table-responsive">
              <table class="table table-sm">
                <thead>
                  <tr>
                    <th>Month</th>
                    <th>Slots</th>
                    <th>Bookings</th>
                  </tr>
                </thead>
                <tbody>
                  <tr
                    v-for="row in report.monthly_summary || []"
                    :key="row.month"
                  >
                    <td>{{ row.month }}</td>
                    <td>{{ row.slots }}</td>
                    <td>{{ row.bookings }}</td>
                  </tr>
                  <tr v-if="!report.monthly_summary?.length">
                    <td colspan="3" class="text-secondary">No historical slot data.</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>

      <!-- Student Performance -->
      <div class="col-12">
        <div class="card">
          <div class="card-body">
            <h5 class="h6 fw-bold">Student Performance</h5>
            <div class="table-responsive">
              <table class="table table-sm">
                <thead>
                  <tr>
                    <th>Student</th>
                    <th>Result</th>
                    <th>Performance</th>
                  </tr>
                </thead>
                <tbody>
                  <tr
                    v-for="(row, index) in report.student_performance || []"
                    :key="`${row.student_name}-${index}`"
                  >
                    <td>{{ row.student_name }}</td>
                    <td>{{ row.percentage }}%</td>
                    <td>
                      <div class="progress">
                        <div
                          class="progress-bar"
                          :style="{ width: clampPercentage(row.percentage) }"
                        />
                      </div>
                    </td>
                  </tr>
                  <tr v-if="!report.student_performance?.length">
                    <td colspan="3" class="text-secondary">No evaluated students.</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { apiRequest } from '../../services/api.js'

/* ------------------------------------------------------------------
 * State
 * ---------------------------------------------------------------- */
const report = ref({})
const loading = ref(false)
const error = ref('')

/* ------------------------------------------------------------------
 * Derived data
 * ---------------------------------------------------------------- */
const summaryCards = computed(() => [
  {
    label: 'Examinations Conducted',
    value: report.value.examinations_conducted || 0
  },
  {
    label: 'Students Evaluated',
    value: report.value.students_evaluated || 0
  },
  {
    label: 'Completed Bookings',
    value: report.value.completed_bookings || 0
  },
  {
    label: 'Pending Evaluations',
    value: report.value.pending_evaluations || 0
  }
])

/* ------------------------------------------------------------------
 * Helpers
 * ---------------------------------------------------------------- */

/**
 * Convert a count into a percentage of the total across all rows.
 * Returns a CSS-friendly string like "42.5%". Falls back to "0%"
 * when the total is zero.
 */
function percentOfTotal(value, rows = []) {
  const total = rows.reduce((sum, row) => sum + row.count, 0)
  return total ? `${(value / total) * 100}%` : '0%'
}

/**
 * Clamp a numeric percentage between 0 and 100 and return it
 * as a CSS width value.
 */
function clampPercentage(value) {
  return `${Math.min(100, Math.max(0, value))}%`
}

/* ------------------------------------------------------------------
 * Data loading
 * ---------------------------------------------------------------- */
async function loadReports() {
  loading.value = true
  error.value = ''

  try {
    report.value = await apiRequest('/admin/reports')
  } catch (err) {
    error.value = err.message || 'Could not load reports.'
  } finally {
    loading.value = false
  }
}

onMounted(loadReports)
</script>