
<template>
    <div class="container-fluid p-3">

        <!-- Breadcrumb and Heading -->
        <div class="mb-3">
            <div class="text-secondary small mb-1">
                Home / admin / Dashboard
            </div>

            <h6 class="fw-bold mb-0">Dashboard</h6>
        </div>

        <!-- Summary Cards -->
        <div class="row g-3 mb-3">

            <div class="col-12 col-sm-6 col-lg-4 col-xl-2">
                <div class="card h-100">
                    <div class="card-body py-3">
                        <div class="small">Total Courses</div>
                        <h3 class="fw-bold mb-0">
                            {{ dashboard.total_courses ?? 0 }}
                        </h3>
                    </div>
                </div>
            </div>

            <div class="col-12 col-sm-6 col-lg-4 col-xl-2">
                <div class="card h-100">
                    <div class="card-body py-3">
                        <div class="small">Total Examinations</div>
                        <h3 class="fw-bold mb-0">
                            {{ dashboard.total_examinations ?? 0 }}
                        </h3>
                    </div>
                </div>
            </div>

            <div class="col-12 col-sm-6 col-lg-4 col-xl-2">
                <div class="card h-100">
                    <div class="card-body py-3">
                        <div class="small">Total Students</div>
                        <h3 class="fw-bold mb-0">
                            {{ dashboard.total_students ?? 0 }}
                        </h3>
                    </div>
                </div>
            </div>

            <div class="col-12 col-sm-6 col-lg-4 col-xl-2">
                <div class="card h-100">
                    <div class="card-body py-3">
                        <div class="small">Total Examiners</div>
                        <h3 class="fw-bold mb-0">
                            {{ dashboard.total_examiners ?? 0 }}
                        </h3>
                    </div>
                </div>
            </div>

            <div class="col-12 col-sm-6 col-lg-4 col-xl-2">
                <div class="card h-100">
                    <div class="card-body py-3">
                        <div class="small">Total Slots</div>
                        <h3 class="fw-bold mb-0">
                            {{ dashboard.total_slots ?? 0 }}
                        </h3>
                    </div>
                </div>
            </div>

            <div class="col-12 col-sm-6 col-lg-4 col-xl-2">
                <div class="card h-100">
                    <div class="card-body py-3">
                        <div class="small">Total Bookings</div>
                        <h3 class="fw-bold mb-0">
                            {{ dashboard.total_bookings ?? 0 }}
                        </h3>
                    </div>
                </div>
            </div>

        </div>

        <!-- Recent Activities -->
        <div class="card mb-3">
            <div class="card-body">

                <h6 class="fw-bold mb-2">Recent Activities</h6>

                <div class="table-responsive">
                    <table class="table table-sm align-middle mb-0">

                        <thead class="table-light">
                            <tr>
                                <th>Date</th>
                                <th>Activity</th>
                                <th>Performed By</th>
                            </tr>
                        </thead>

                        <tbody>
                            <tr
                                v-for="(activity, index) in recentActivities"
                                :key="activity.id || index"
                            >
                                <td>{{ activity.date }}</td>
                                <td>{{ activity.activity }}</td>
                                <td>{{ activity.performed_by }}</td>
                            </tr>

                            <tr v-if="recentActivities.length === 0">
                                <td
                                    colspan="3"
                                    class="text-center text-secondary py-3"
                                >
                                    No recent activities available.
                                </td>
                            </tr>
                        </tbody>

                    </table>
                </div>

            </div>
        </div>

        <!-- Dashboard Charts -->
        <div class="row g-3">

            <!-- Examination Status -->
            <div class="col-12 col-lg-6">
                <div class="card h-100">
                    <div class="card-body">

                        <h6 class="fw-bold mb-3">
                            Examinations by Status
                        </h6>

                        <div
                            v-for="item in examinationStatuses"
                            :key="item.status"
                            class="mb-3"
                        >
                            <div class="d-flex justify-content-between small mb-1">
                                <span>{{ item.status }}</span>
                                <span>{{ item.count }}</span>
                            </div>

                            <div class="progress">
                                <div
                                    class="progress-bar"
                                    role="progressbar"
                                    :style="{ width: getExamWidth(item.count) }"
                                ></div>
                            </div>
                        </div>

                        <p
                            v-if="examinationStatuses.length === 0"
                            class="text-secondary small mb-0"
                        >
                            No examination data available.
                        </p>

                    </div>
                </div>
            </div>

            <!-- Booking Status -->
            <div class="col-12 col-lg-6">
                <div class="card h-100">
                    <div class="card-body">

                        <h6 class="fw-bold mb-3">
                            Bookings by Status
                        </h6>

                        <div
                            v-for="item in bookingStatuses"
                            :key="item.status"
                            class="mb-3"
                        >
                            <div class="d-flex justify-content-between small mb-1">
                                <span>{{ item.status }}</span>
                                <span>{{ item.count }}</span>
                            </div>

                            <div class="progress">
                                <div
                                    class="progress-bar bg-success"
                                    role="progressbar"
                                    :style="{ width: getBookingWidth(item.count) }"
                                ></div>
                            </div>
                        </div>

                        <p
                            v-if="bookingStatuses.length === 0"
                            class="text-secondary small mb-0"
                        >
                            No booking data available.
                        </p>

                    </div>
                </div>
            </div>

        </div>

        <!-- Error Message -->
        <div v-if="error" class="alert alert-danger mt-3 mb-0">
            {{ error }}
        </div>

    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { apiRequest } from '../services/api'

const dashboard = ref({})
const recentActivities = ref([])
const examinationStatuses = ref([])
const bookingStatuses = ref([])
const error = ref('')

function getExamWidth(count) {
    const total = examinationStatuses.value.reduce(
        (sum, item) => sum + item.count,
        0
    )

    return total ? `${(count / total) * 100}%` : '0%'
}

function getBookingWidth(count) {
    const total = bookingStatuses.value.reduce(
        (sum, item) => sum + item.count,
        0
    )

    return total ? `${(count / total) * 100}%` : '0%'
}

function loadDashboard() {
    apiRequest('/admin/dashboard')
        .then((data) => {
            dashboard.value = data
            recentActivities.value = data.recent_activities || []
            examinationStatuses.value = data.examination_statuses || []
            bookingStatuses.value = data.booking_statuses || []
        })
        .catch((err) => {
            error.value = err.message || 'Unable to load dashboard data.'
        })
}

onMounted(() => {
    loadDashboard()
})
</script>
