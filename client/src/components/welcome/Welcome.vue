<template>
  <div :style="{display: 'grid',alignItems:'center',height: innerHeight+'px'}">
    <div>
      <div style="font-size: 40px;line-height: 52px;text-align: center;font-weight: 600;display: flex;justify-content: center;align-items: center">
        <el-image
            style="width: 40px; height: 40px;border-radius: 50%;background: #002857"
            src="/images/defaults/rptu.png"
            :zoom-rate="1.2"
            :max-scale="7"
            :min-scale="0.2"
            :initial-index="4"
            fit="cover"
        />Adiutor
      </div>
      <div style="font-size: 20px;line-height: 26px;text-align: center;font-weight: 400">
        Your daily AI companion
        <small style="position: absolute;bottom: 0;left:0;right:0;font-size: 15px;font-style: italic;font-family: 'Droid Serif',-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,'Helvetica Neue',Arial,sans-serif,'Apple Color Emoji','Segoe UI Emoji','Segoe UI Symbol','Noto Color Emoji'">
          „As far as the customer is concerned, the interface is the product.“  ~ Jef Raskin
        </small>
      </div>
    </div>
  </div>
</template>