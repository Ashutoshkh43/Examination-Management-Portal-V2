<template>
  <!-- Main container centering content on the screen -->
  <div class="container d-flex flex-column align-items-center justify-content-center min-vh-100 text-center">
    
    <!-- Heading with margin-bottom -->
    <h1 class="display-5 fw-bold mb-4 text-primary">
      This is the homepage of the Examination Portal App
    </h1>

    <!-- Action container for buttons -->
    <div class="d-grid gap-3 col-12 col-sm-6 col-md-4 mx-auto">
      
      <!-- Login Button: RouterLink surrounds the button so the entire element is clickable -->
      <RouterLink to="/login" class="text-decoration-none">
        <button type="button" class="btn btn-primary btn-lg w-100 shadow-sm">
          Login
        </button>
      </RouterLink>

      <!-- Register Button: Styled as an outline button for visual hierarchy -->
      <RouterLink to="/register" class="text-decoration-none">
        <button type="button" class="btn btn-outline-secondary btn-lg w-100 shadow-sm">
          Register
        </button>
      </RouterLink>

    </div>
  </div>
</template>
