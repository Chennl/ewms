 
 
  
    
    var vm = new Vue({
         el:'#app',
         data(){
           return {
            visible:false,
            msg:'hello msg',
            title:' <h3>菜鸟教程</h3>',
            age:2019,
            num:10,
            use:false,
            ok:true,
            message:'abcd',
            id:1,
            seen:true,
            tableData: [],
            loading:true,
            errored:false,
            search:''
         }
         },
         methods: {
            dataFormatter:function(row,column){
              return moment(row.last_seen,moment.ISO_8601).format('YYYY-MM-DD hh:mm:ss');
              },
            handleEdit: function(index,row){
              console.log('edit',index,row);
              this.$set(row,'isEgdit',true);
            },
            handleDelete: function(index,row){
              console.log('delete',index,row)
            },
             say:function(){ alert(this.title);},
             handleChange:function(value){console.log(value);}
         },
         mounted() {
             axios
             .get('/api/users')
             .then(response=>{
               this.tableData = response.data.data;
               console.log(response.data)
               })
             .catch(error=>{
               console.log(error);
               this.errored = true;
               })
               .finally(()=>this.loading = false)
         },
     })
 